import asyncio
import sys
import traceback
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Encapsulate app creation
def create_app():
    from app.server import create_server
    from app.prompt import register_prompts
    from app.resource  import register_resources
    from app.tools import register_tools
    
    app = create_server()
    register_tools(app)
    register_prompts(app)
    register_resources(app)
    return app

async def main():
    try:
        app = create_app()
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception:
        # Catch errors during app creation or run
        with open("server_error.log", "w") as f:
            f.write(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        # Catch errors outside of main (e.g. asyncio run failure)
        with open("server_error.log", "w") as f:
            f.write(traceback.format_exc())
        sys.exit(1)



