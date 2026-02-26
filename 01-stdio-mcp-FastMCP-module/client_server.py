import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import os

async def run_client():
    # parameters to connect to our server.py
    # We tell the client: "Run this command to start the server"
    server_params = StdioServerParameters(
        command=sys.executable,  # The current python interpreter
        args=["mcp_server.py"],      # The script to run
        env=os.environ.copy()    # Pass current environment (important for venv)
    )

    print(f"🔌 Connecting to server using {sys.executable}...")
    
    # Establish the connection context
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✅ Connected to server!")

            # List available tools
            print("\n📋 Available Tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call the 'get_system_info' tool
            print("\n💻 Calling 'get_system_info'...")
            result = await session.call_tool("get_system_info")
            print("Response:")
            print(result.content[0].text)

            # Call the 'echo' tool
            print("\n🗣️ Calling 'echo' with message 'Hello MCP!'...")
            result = await session.call_tool("echo", arguments={"message": "Hello MCP!"})
            print("Response:")
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run_client())
