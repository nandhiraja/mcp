from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import sys
import shutil

# Path to python executable
python_executable = sys.executable
# Path to the server script
server_script = "server.py"

async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command=python_executable,
        args=[server_script],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()

            # 1. Add a todo
            print("--- Adding a todo ---")
            result = await session.call_tool("add_todo", arguments={"title": "Buy milk"})
            print(result.content[0].text)

            # 2. List todos (using resource)
            print("\n--- Listing todos ---")
            # We don't have direct resource reading in ClientSession high-level API easily for this demo in one line
            # usually, but let's check tools first. 
            # Actually, `read_resource` is a method on session.
            # Resources are accessed by URI.
            try:
                # Based on FastMCP default resource format. We defined 'todo://list' in server.py
                # Note: FastMCP might need the template syntax or direct URI. 
                # Let's try reading the resource.
                resource_content = await session.read_resource("todo://list")
                print(f"Todos: {resource_content.contents[0].text}")
            except Exception as e:
                print(f"Error reading resource: {e}")

            # 3. Add another todo
            await session.call_tool("add_todo", arguments={"title": "Walk the dog"})
            
            # 4. List again
            print("\n--- Listing todos after adding another ---")
            resource_content = await session.read_resource("todo://list")
            print(f"Todos: {resource_content.contents[0].text}")

            # 5. Complete a todo (Assuming ID 1 is the first one, since we just initialized DB)
            # We need to parse the JSON really to get IDs, but for simplicity let's assume ID 1.
            print("\n--- Completing todo with ID 1 ---")
            result = await session.call_tool("complete_todo", arguments={"todo_id": 1})
            print(result.content[0].text)

            # 6. List final state
            print("\n--- Listing todos after completion ---")
            resource_content = await session.read_resource("todo://list")
            print(f"Todos: {resource_content.contents[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
