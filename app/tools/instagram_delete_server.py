from app.tools.base import create_stub_server, run_sse, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="instagram_delete_server",
    tool_name="instagram_delete",
    description="owner-authorized take-down of a live piece",
    input_schema={
        "type": "object",
        "properties": {
            "media_id": {"type": "string"}
        },
        "required": ["media_id"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["instagram_delete"],
    stub_response={"external_media_id": "stub", "action": "delete", "done_at": "2026-07-01T00:00:00Z"}
)

if __name__ == "__main__":
    run_sse(server)
