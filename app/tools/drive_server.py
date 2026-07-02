from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="drive_server",
    tool_name="drive",
    description="store/host assets, byte-serving for auto-publish, previews",
    input_schema={
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "file_id": {"type": "string"}
        },
        "required": ["action"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["drive"],
    stub_response={"file_id": "stub", "drive_url": "stub", "byte_url": "stub", "mime_type": "image/jpeg", "bytes": 1024}
)

if __name__ == "__main__":
    run_stdio(server)
