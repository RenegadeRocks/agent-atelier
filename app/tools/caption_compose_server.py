from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="caption_compose_server",
    tool_name="caption_compose",
    description="brand typography compositing",
    input_schema={
        "type": "object",
        "properties": {
            "image_url": {"type": "string"},
            "caption": {"type": "string"}
        },
        "required": ["image_url", "caption"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["caption_compose"],
    stub_response={"asset_url": "stub", "ocr_text_free": True, "scrim_applied": True, "width": 1080, "height": 1920, "short_edge_px": 1080}
)

if __name__ == "__main__":
    run_stdio(server)
