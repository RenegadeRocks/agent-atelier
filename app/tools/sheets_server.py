from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="sheets_server",
    tool_name="sheets",
    description="calendar, ledger, queue, async approval, append-only audit",
    input_schema={
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "range_name": {"type": "string"}
        },
        "required": ["action"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["sheets"],
    stub_response={"ok": True, "updated_range": "stub", "row_id": "stub", "values": []}
)

if __name__ == "__main__":
    run_stdio(server)
