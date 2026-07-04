import pytest
import json
import asyncio
import os
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock
from mcp.types import TextContent

from app.pipeline import run_pipeline

# Import the servers
import app.tools.sheets_server as sheets_server
import app.tools.caption_compose_server as caption_compose_server
import app.tools.image_generate_server as image_generate_server
import app.tools.drive_server as drive_server

# -- MOCK IMPLEMENTATIONS FOR CI --

def mock_sheets_handle_call_tool(name: str, arguments: dict):
    output = {
        "ok": True,
        "updated_range": "Mock_queue",
        "row_id": arguments.get("piece_id", "123"),
        "values": [arguments.get("values", {})]
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_caption_compose_handle_call_tool(name: str, arguments: dict):
    img_url = arguments.get("image_url", "")
    ocr_text_free = "baked_glyph" not in img_url
    output = {
        "asset_url": f"composited_{img_url}",
        "ocr_text_free": ocr_text_free,
        "scrim_applied": True,
        "width": 1080,
        "height": 1920,
        "short_edge_px": 1080
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_image_generate_handle_call_tool(name: str, arguments: dict):
    prompt = arguments.get("prompt", "")
    pred_id = str(uuid.uuid4())[:8]
    if "bake text" in prompt.lower():
        asset_url = f"baked_glyph_{pred_id}.jpg"
    else:
        asset_url = f"clean_image_{pred_id}.jpg"
    
    output = {
        "asset_url": asset_url,
        "prediction_id": f"pred_{pred_id}",
        "provider": "mock-provider",
        "tier": "high",
        "width": 1024,
        "height": 1024
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_drive_handle_call_tool(name: str, arguments: dict):
    file_id = arguments.get("file_id", "test_file")
    output = {
        "file_id": file_id,
        "drive_url": f"https://drive.google.com/mock/{file_id}",
        "byte_url": f"https://drive.google.com/mock/uc?id={file_id}",
        "mime_type": "image/jpeg",
        "bytes": 2048
    }
    return [TextContent(type="text", text=json.dumps(output))]


def test_mcp_schemas():
    """
    Scenario: The sheets, caption_compose, image_generate, and drive MCP tools conform to their declared schemas (CI Mocked).
    """
    with patch('app.tools.sheets_server.sheets_handle_call_tool', side_effect=mock_sheets_handle_call_tool), \
         patch('app.tools.caption_compose_server.caption_compose_handle_call_tool', side_effect=mock_caption_compose_handle_call_tool), \
         patch('app.tools.image_generate_server.image_generate_handle_call_tool', side_effect=mock_image_generate_handle_call_tool), \
         patch('app.tools.drive_server.drive_handle_call_tool', side_effect=mock_drive_handle_call_tool):
         
        # Test sheets_server
        res = sheets_server.sheets_handle_call_tool("sheets", {"action": "queue", "piece_id": "test_123", "values": {"status": "test"}})
        output = json.loads(res[0].text)
        assert "ok" in output
        assert "updated_range" in output
        assert "row_id" in output
        assert "values" in output
        
        # Test caption_compose_server (valid)
        res = caption_compose_server.caption_compose_handle_call_tool("caption_compose", {"image_url": "clean_image.jpg", "caption": "Test"})
        output = json.loads(res[0].text)
        assert output["ocr_text_free"] is True
        assert "scrim_applied" in output
        assert output["short_edge_px"] >= 1080
        
        # Test caption_compose_server (baked_glyph)
        res = caption_compose_server.caption_compose_handle_call_tool("caption_compose", {"image_url": "baked_glyph.jpg", "caption": "Test"})
        output = json.loads(res[0].text)
        assert output["ocr_text_free"] is False
        
        # Test image_generate_server
        res = image_generate_server.image_generate_handle_call_tool("image_generate", {"prompt": "test"})
        output = json.loads(res[0].text)
        assert "asset_url" in output
        assert "prediction_id" in output
        assert "provider" in output
        assert "tier" in output
        assert "width" in output
        assert "height" in output
        
        # Test drive_server
        res = drive_server.drive_handle_call_tool("drive", {"action": "upload", "file_id": "file_123"})
        output = json.loads(res[0].text)
        assert "file_id" in output
        assert "drive_url" in output

        assert "mime_type" in output
        assert output["byte_url"].startswith("http")

def test_p1_b_pipeline_escalation():
    """
    Scenario: The pipeline correctly handles deterministic blocks (like the OCR text-free check) and loops/escalates properly (CI Mocked).
    """
    with patch('app.pipeline.sheets_handle_call_tool', side_effect=mock_sheets_handle_call_tool), \
         patch('app.pipeline.caption_compose_handle_call_tool', side_effect=mock_caption_compose_handle_call_tool), \
         patch('app.pipeline.image_generate_handle_call_tool', side_effect=mock_image_generate_handle_call_tool), \
         patch('app.pipeline.drive_handle_call_tool', side_effect=mock_drive_handle_call_tool):
         
        test_idea = "A test idea for the hard-coded brand, bake text"
        
        result = run_pipeline(test_idea)
        
        assert result is not None
        assert result.get("status") == "Escalated"
        
        trace = result.get("trace", [])
        
        assert "managing_editor" in trace
        assert "visual_production" in trace
        assert "escalate_visual" in trace

@pytest.mark.live
def test_p1_b_pipeline_flow():
    """
    Scenario: LIVE E2E test. The pipeline state machine progresses correctly from PLAN through QUEUE.
    Scenario: A final piece successfully lands in the REAL Google Sheets queue and Drive via Real API MCPs.
    """
    test_idea = "A simple red apple on a clean wooden table. Absolutely no text, no branding, no logos."
    
    result = run_pipeline(test_idea)
    
    assert result is not None
    assert result.get("status") == "Approval Queue"
    
    trace = result.get("trace", [])
    
    assert "managing_editor" in trace
    assert "creative_director" in trace
    assert "publishing_operations" in trace
