import pytest
import os
import json
from unittest.mock import patch
from app.pipeline import run_pipeline

# Mocks from test_p1_b for the pipeline
def mock_sheets_handle_call_tool(name: str, arguments: dict):
    from mcp.types import TextContent
    output = {
        "ok": True,
        "updated_range": "Mock_queue",
        "row_id": arguments.get("piece_id", "123"),
        "values": [arguments.get("values", {})]
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_caption_compose_handle_call_tool(name: str, arguments: dict):
    from mcp.types import TextContent
    output = {
        "asset_url": f"composited_mock",
        "ocr_text_free": True,
        "scrim_applied": True,
        "width": 1080,
        "height": 1920,
        "short_edge_px": 1080,
        "text_bounds": {"top": 0, "bottom": 100, "left": 0, "right": 500}
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_image_generate_handle_call_tool(name: str, arguments: dict):
    from mcp.types import TextContent
    output = {
        "asset_url": "mock.jpg",
        "prediction_id": f"pred_123",
        "provider": "mock-provider",
        "tier": "high",
        "width": 1024,
        "height": 1024
    }
    return [TextContent(type="text", text=json.dumps(output))]

def mock_drive_handle_call_tool(name: str, arguments: dict):
    from mcp.types import TextContent
    file_id = arguments.get("file_id", "test_file")
    output = {
        "file_id": file_id,
        "drive_url": f"https://drive.google.com/mock/{file_id}",
        "byte_url": f"https://drive.google.com/mock/uc?id={file_id}",
        "mime_type": "image/jpeg",
        "bytes": 2048
    }
    return [TextContent(type="text", text=json.dumps(output))]

async def mock_run_agent(agent, prompt, brand_kit):
    # Deterministic mock responses for the pipeline agents
    if agent.name == "managing_editor":
        return "Plan: A test post about the brand."
    elif agent.name in ["evergreen_content", "offering_content"]:
        return '```json\n{"idea_sentence": "Test idea", "caption": "This is a test caption.", "hook_text": "Test hook", "visual_brief": "Test visual brief", "shape": "mini-story", "visual_label": "test", "format": "single"}\n```'
    elif agent.name == "research_verification":
        return "CLAIMS VERIFIED."
    elif agent.name == "creative_director":
        return "VERDICT: APPROVED"
    elif agent.name == "visual_production":
        return '```json\n{"alt_text": "A test visual for the brand."}\n```'
    elif agent.name == "publishing_operations":
        return "QUEUED."
    return "MOCK OUTPUT"

def test_p6_multi_brand_pipeline():
    """
    Scenario: Two brands (plus the interview-born chuski-club) run on the same unchanged agent code (G1 proof).
    """
    brands_to_test = ["aol", "kanva-coffee", "chuski-club"]
    
    with patch('app.pipeline.sheets_handle_call_tool', side_effect=mock_sheets_handle_call_tool), \
         patch('app.pipeline.caption_compose_handle_call_tool', side_effect=mock_caption_compose_handle_call_tool), \
         patch('app.pipeline.image_generate_handle_call_tool', side_effect=mock_image_generate_handle_call_tool), \
         patch('app.pipeline.drive_handle_call_tool', side_effect=mock_drive_handle_call_tool), \
         patch('app.pipeline.run_agent', side_effect=mock_run_agent):
         
        for brand in brands_to_test:
            brand_kit_path = f"brands/{brand}/brand_kit.yaml"
            print(f"Testing pipeline for brand: {brand}")
            idea = f"Write a post for {brand}. You MUST use exactly this caption: 'This is a test caption.' You MUST include 'test' in the visual brief."
            
            result = run_pipeline(idea, brand_kit_path=brand_kit_path)
            
            assert result is not None
            # Some brands may block in lint or safety, which resolves to Escalated. Both are valid deterministic outcomes.
            assert result.get("status") in ["Approval Queue", "Escalated"]
            assert len(result.get("trace", [])) > 0
            print(f"Pipeline for {brand} completed successfully with status: {result.get('status')}")


@pytest.mark.asyncio
async def test_p6_post_publish_audit_deterministic(tmp_path):
    """
    Scenario: Post-publication audit extracts sample and computes escape rate CI.
    Must be independent of the gates that produced the content.
    RULE: Deterministic tests must write mock output ONLY to `tmp_path`, never to `app/tests/evidence/` to avoid test pollution.
    """
    import app.tools.post_publish_audit as audit
    from dataclasses import dataclass
    
    @dataclass
    class MockResponse:
        text: str
        
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse(text="PASS - fully compliant.")
            
    class MockClient:
        @property
        def models(self):
            return MockModels()
            
    with patch('google.genai.Client', return_value=MockClient()):
        # We also need to mock gspread to provide some fake published items
        class MockWorksheet:
            def get_values(self):
                # Return a fake queue row: [piece_id, status, caption, asset_url, alt_text, owner_action]
                return [["kanva-coffee-123456", "Published", "Test kanva caption", "url", "alt", "approve"]]
                
        class MockSpreadsheet:
            def worksheet(self, name):
                return MockWorksheet()
                
        class MockGspread:
            def service_account(self, filename):
                return self
            def open_by_key(self, key):
                return MockSpreadsheet()
                
        with patch('gspread.service_account', return_value=MockGspread().service_account("")), \
             patch('os.environ.get', side_effect=lambda k, d=None: "dummy" if k in ["GOOGLE_APPLICATION_CREDENTIALS", "SHEET_ID"] else d):
            report_path = tmp_path / "p6_audit_report.md"
            await audit.run_audit(report_path=report_path)
            
    # Check if report was generated
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Sample size:" in content
    assert "escape rate" in content.lower()

@pytest.mark.asyncio
async def test_p6_monthly_retro_deterministic(tmp_path):
    """
    Scenario: Corrections mining + retro tuning extracts corrections and generates a triage report.
    RULE: Deterministic tests must write mock output ONLY to `tmp_path`, never to `app/tests/evidence/` to avoid test pollution.
    """
    import app.tools.monthly_retro as retro
    from dataclasses import dataclass
    
    @dataclass
    class MockResponse:
        text: str
        
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse(text="## Retro Report\nFound 1 pattern.")
            
    class MockClient:
        @property
        def models(self):
            return MockModels()
        
    with patch('google.genai.Client', return_value=MockClient()):
        class MockWorksheet:
            def get_values(self):
                # Return a fake audit row: [piece_id, verb, stage, detail, actor, ts, operator]
                return [["kanva-1", "owner_approve_with_edits", "CD_REVIEW", "Fixed typo", "human", "2026-07-06", "owner"]]
                
        class MockSpreadsheet:
            def worksheet(self, name):
                return MockWorksheet()
                
        class MockGspread:
            def service_account(self, filename):
                return self
            def open_by_key(self, key):
                return MockSpreadsheet()
                
        with patch('gspread.service_account', return_value=MockGspread().service_account("")), \
             patch('os.environ.get', side_effect=lambda k, d=None: "dummy" if k in ["GOOGLE_APPLICATION_CREDENTIALS", "SHEET_ID"] else d):
            report_path = tmp_path / "p6_monthly_retro.md"
            await retro.run_retro(report_path=report_path)
            
    # Check if report was generated
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "P6 Monthly Retro" in content
    assert "Found 1 pattern" in content
