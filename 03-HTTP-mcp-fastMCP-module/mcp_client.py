import asyncio
from fastmcp import Client



async def main():
    
    # Connect to the server's HTTP/SSE endpoint
    async with Client("http://127.0.0.1:8000/sse") as client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        result = await client.call_tool("say_hello", {"name": "Developer"})
        print(f"Server response: {result.content[0].text}, \n\n{result.structured_content}")




if __name__ == "__main__":
    asyncio.run(main())