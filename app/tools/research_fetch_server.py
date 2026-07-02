from app.tools.base import create_stub_server, run_sse, ALL_OUTPUT_SCHEMAS

server = create_stub_server(
    server_name="research_fetch_server",
    tool_name="research_fetch",
    description="sanitized, allowlist-bound source retrieval + grounding",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    output_schema=ALL_OUTPUT_SCHEMAS["research_fetch"],
    stub_response={"source_url": "stub", "fetched_text": "stub", "source_hash": "stub", "fetched_at": "2026-07-01T00:00:00Z"}
)

if __name__ == "__main__":
    run_sse(server)
