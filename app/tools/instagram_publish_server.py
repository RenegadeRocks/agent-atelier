from app.tools.base import create_stub_server, run_sse, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="instagram_publish_server",
    tool_name="instagram_publish",
    description="publish to Instagram (the only launch adapter)",
    input_schema={
        "type": "object",
        "properties": {
            "media_url": {"type": "string"},
            "caption": {"type": "string"}
        },
        "required": ["media_url", "caption"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["instagram_publish"],
    stub_response={"external_media_id": "stub", "posted_permalink": "stub", "posted_at": "2026-07-01T00:00:00Z", "publish_method": "auto", "first_comment_posted": True}
)

if __name__ == "__main__":
    run_sse(server)
