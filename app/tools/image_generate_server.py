from app.tools.base import create_stub_server, run_stdio, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="image_generate_server",
    tool_name="image_generate",
    description="text-free image generation",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string"},
            "provider": {"type": "string", "default": "gemini_image_pro"}
        },
        "required": ["prompt"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["image_generate"],
    stub_response={"asset_url": "stub", "prediction_id": "stub", "provider": "gemini_image_pro", "tier": "stub", "width": 1024, "height": 1024}
)

if __name__ == "__main__":
    run_stdio(server)
