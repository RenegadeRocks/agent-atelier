from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="handoff_export_server",
    tool_name="handoff_export",
    description="materialize the manual Post Kit",
    input_schema={
        "type": "object",
        "properties": {
            "piece_id": {"type": "string"}
        },
        "required": ["piece_id"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["handoff_export"],
    stub_response={"handoff_bundle_ref": "stub", "folder_url": "stub", "qr_url": "stub", "slide_count": 1, "checklist": [], "export_precheck_pass": True}
)

if __name__ == "__main__":
    run_stdio(server)
