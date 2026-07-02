from app.tools.base import create_stub_server, run_sse, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="instagram_caption_edit_server",
    tool_name="instagram_caption_edit",
    description="owner-authorized correct-in-place of a live piece",
    input_schema={
        "type": "object",
        "properties": {
            "media_id": {"type": "string"},
            "new_caption": {"type": "string"}
        },
        "required": ["media_id", "new_caption"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["instagram_caption_edit"],
    stub_response={"external_media_id": "stub", "action": "caption_edit", "done_at": "2026-07-01T00:00:00Z"}
)

if __name__ == "__main__":
    run_sse(server)
