from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="calendar_server",
    tool_name="calendar",
    description="schedule slots",
    input_schema={
        "type": "object",
        "properties": {
            "action": {"type": "string"}
        },
        "required": ["action"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["calendar"],
    stub_response={"event_id": "stub", "start": "2026-07-01T00:00:00Z", "end": "2026-07-01T01:00:00Z"}
)

if __name__ == "__main__":
    run_stdio(server)
