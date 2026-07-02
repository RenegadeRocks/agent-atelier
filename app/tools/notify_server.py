import json
from app.tools.base import create_stub_server, run_sse, ALL_OUTPUT_SCHEMAS, NOTIFY_INPUT_SCHEMA_FILE

with open(NOTIFY_INPUT_SCHEMA_FILE) as f:
    notify_input_schema = json.load(f)

server = create_stub_server(
    server_name="notify_server",
    tool_name="notify",
    description="owner-reaching alerts, digests & escalations",
    input_schema=notify_input_schema,
    output_schema=ALL_OUTPUT_SCHEMAS["notify"],
    stub_response={"notification_id": "stub", "state": "sent", "dedup_key": "stub", "sent_at": "2026-07-01T00:00:00Z"}
)

if __name__ == "__main__":
    run_sse(server)
