import json
from pathlib import Path

def test_p0_mcp_stubs_match_authored_schemas():
    """
    Scenario: P0 Architecture Validation - exact schema matching
      Given the 11 Agent Atelier MCP server stubs
      When we inspect their declared output schemas
      Then each stub's declared output schema must exactly match the authored JSON schema
      And the notify input schema must exactly match notify_payload.schema.json
    """
    from app.tools import (
        image_generate_server,
        caption_compose_server,
        drive_server,
        sheets_server,
        research_fetch_server,
        instagram_publish_server,
        instagram_caption_edit_server,
        instagram_delete_server,
        notify_server,
        calendar_server,
        handoff_export_server
    )
    
    servers = [
        image_generate_server.server,
        caption_compose_server.server,
        drive_server.server,
        sheets_server.server,
        research_fetch_server.server,
        instagram_publish_server.server,
        instagram_caption_edit_server.server,
        instagram_delete_server.server,
        notify_server.server,
        calendar_server.server,
        handoff_export_server.server
    ]
    
    REPO_ROOT = Path(__file__).parent.parent.parent
    OUTPUTS_SCHEMA_FILE = REPO_ROOT / "specs" / "schemas" / "mcp_tool_outputs.schema.json"
    NOTIFY_INPUT_SCHEMA_FILE = REPO_ROOT / "specs" / "schemas" / "notify_payload.schema.json"
    
    with open(OUTPUTS_SCHEMA_FILE) as f:
        outputs_data = json.load(f)
    all_output_schemas = outputs_data["properties"]["tools"]["properties"]
    
    with open(NOTIFY_INPUT_SCHEMA_FILE) as f:
        notify_input_schema = json.load(f)
        
    found_tools = set()
    
    for srv in servers:
        tool_name = srv.tool_name
        found_tools.add(tool_name)
        
        # Verify output schema exact match
        expected_out = all_output_schemas[tool_name]
        assert srv.declared_output_schema == expected_out, f"{tool_name} output schema does not exactly match the authored schema."
        
        # Verify notify input schema exact match
        if tool_name == "notify":
            assert srv.input_schema == notify_input_schema, "notify input schema does not exactly match the authored notify_payload.schema.json."

    expected_tools = {
        "image_generate",
        "caption_compose",
        "drive",
        "sheets",
        "research_fetch",
        "instagram_publish",
        "instagram_caption_edit",
        "instagram_delete",
        "notify",
        "calendar",
        "handoff_export"
    }
    
    missing = expected_tools - found_tools
    assert not missing, f"Missing expected MCP tools: {missing}"
