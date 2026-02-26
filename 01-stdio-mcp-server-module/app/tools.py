from mcp.types import Tool, TextContent
from mcp.server import Server
import platform
import sys
import datetime

# --- Tool Functions  ---

async def add_numbers(args: dict) -> list[TextContent]:

    result = int(args.get("a", 0)) + int(args.get("b", 0))
    return [TextContent(type="text", text=str(result))]

async def mul_numbers(args: dict) -> list[TextContent]:

    result = int(args.get("a", 0)) * int(args.get("b", 0))
    return [TextContent(type="text", text=str(result))]

# ==================================================================

async def sys_config(args: dict) -> list[TextContent]:
    info = [
        f"System: {platform.system()} {platform.release()}",
        f"Python: {sys.version.split()[0]}",
        f"Time: {datetime.datetime.now().isoformat()}"
    ]
    return [TextContent(type="text", text="\n".join(info))]

# --- Registration ---

def register_tools(server: Server):
    
    TOOL_MAP = {
        "add_numbers": add_numbers,
        "multiply_numbers": mul_numbers,
        "get_status": sys_config
    }

    @server.list_tools()    
    async def handle_tool_list() -> list[Tool]:
        return [
            Tool(
                name="add_numbers",
                description="Add two numbers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer"},
                        "b": {"type": "integer"}
                    },
                    "required": ["a", "b"]
                }
            ),
            Tool(
                name="multiply_numbers",
                description="Multiply two numbers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer"},
                        "b": {"type": "integer"}
                    },
                    "required": ["a", "b"]
                }
            ),
            Tool(
                name="get_status",
                description="Get basic details from system",
                inputSchema={"type": "object", "properties": {}}
            )
        ]




    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
        
        tool_handler = TOOL_MAP.get(name)
        if not tool_handler:
            raise ValueError(f"Tool not found: {name}")
        
        return await tool_handler(arguments or {})