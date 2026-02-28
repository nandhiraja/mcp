from fastmcp import FastMCP

mcp = FastMCP("My-HTTP-Server")

@mcp.tool()
def say_hello(name: str) -> str:
    """A simple tool to greet a user."""
    return f"Hello, {name}! This response came via HTTP."

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)