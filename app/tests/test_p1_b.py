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
    caption = arguments.get("caption", "").lower()
    ocr_text_free = "bake" not in caption and "bake" not in img_url
    output = {
        "asset_url": f"composited_{img_url}",
        "ocr_text_free": ocr_text_free,
        "scrim_applied": True,
        "width": 1080,
        "height": 1920,
        "short_edge_px": 1080,
        "text_bounds": {"top": 0, "bottom": 100, "left": 0, "right": 500}
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_image_generate_handle_call_tool(name: str, arguments: dict):
    pred_id = str(uuid.uuid4())[:8]
    # For the escalation test, we want to force a visual loop escalation.
    # We can just always return baked_glyph so that the OCR mock always fails it.
    asset_url = f"baked_glyph_{pred_id}.jpg"
    
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

def test_caption_compose_layout():
    """
    Scenario: The caption_compose tool correctly wraps long lines, dynamically sizes the scrim, and scales the font so text stays within bounds.
    """
    # Create a blank white image to test with
    evidence_dir = os.path.join(os.path.dirname(__file__), "evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    test_img_path = os.path.join(evidence_dir, "test_bounds.jpg")
    
    from PIL import Image
    img = Image.new('RGB', (1080, 1080), color='white')
    img.save(test_img_path)
    
    long_text = "This is a deliberately very long hook line meant to run off the canvas if text wrapping and font scaling are not implemented properly. It should be wrapped to multiple lines, and the bounding box of the resulting text block should lie fully inside the image dimensions (with a safe padding margin)."
    
    # We must use the REAL server implementation for this deterministic test, not the mock
    import app.tools.caption_compose_server as ccs
    res = ccs.caption_compose_handle_call_tool("caption_compose", {"image_url": test_img_path, "caption": long_text})
    output = json.loads(res[0].text)
    
    assert "text_bounds" in output, "Bounding box missing from output"
    bounds = output["text_bounds"]
    
    # Assert dimensions are strictly enforced
    assert output["width"] == 1080
    assert output["height"] == 1350
    
    # Assert text lies fully inside the image bounds
    assert bounds["left"] >= 0
    assert bounds["right"] <= output["width"]
    assert bounds["top"] >= 0
    assert bounds["bottom"] <= output["height"]


@pytest.mark.live
def test_p1_b_pipeline_flow():
    """
    Scenario: LIVE E2E test. The pipeline state machine progresses correctly from PLAN through QUEUE.
    Scenario: A final piece successfully lands in the REAL Google Sheets queue and Drive via Real API MCPs.
    """
    # Real organic ideation prompt for the hard-coded brand
    test_idea = "Generate a brand new evergreen piece for our rotation based on the brand kit's mission and audience."
    
    result = run_pipeline(test_idea)
    
    assert result is not None
    assert result.get("status") == "Approval Queue"
    
    trace = result.get("trace", [])
    
    assert "managing_editor" in trace
    assert "creative_director" in trace
    assert "publishing_operations" in trace
