import json
from pathlib import Path
from mcp.server import Server
import mcp.types as types

REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUTS_SCHEMA_FILE = REPO_ROOT / "specs" / "schemas" / "mcp_tool_outputs.schema.json"
NOTIFY_INPUT_SCHEMA_FILE = REPO_ROOT / "specs" / "schemas" / "notify_payload.schema.json"

with open(OUTPUTS_SCHEMA_FILE) as f:
    _outputs_data = json.load(f)
ALL_OUTPUT_SCHEMAS = _outputs_data["properties"]["tools"]["properties"]

def create_stub_server(server_name: str, tool_name: str, description: str, input_schema: dict, output_schema: dict, stub_response: dict) -> Server:
    server = Server(server_name)
    server.declared_output_schema = output_schema
    server.tool_name = tool_name
    server.input_schema = input_schema
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=tool_name,
                description=description,
                inputSchema=input_schema
            )
        ]
        
    @server.call_tool()
    async def handle_call_tool(name_req: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name_req != tool_name:
            raise ValueError(f"Unknown tool: {name_req}")
        return [
            types.TextContent(
                type="text",
                text=json.dumps(stub_response)
            )
        ]
        
    return server

def run_stdio(server: Server):
    import asyncio
    import mcp.server.stdio
    async def _run():
        async with mcp.server.stdio.stdio_server() as (read, write):
            from mcp.server import Server
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(_run())

def run_sse(server: Server):
    # Stub for SSE transport
    print(f"Starting SSE server for {server.name}...")
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route
    from mcp.server.sse import SseServerTransport
    
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
            
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
        
    app = Starlette(routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ])
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
