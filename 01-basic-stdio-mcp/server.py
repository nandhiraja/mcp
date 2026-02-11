from mcp.server.fastmcp import FastMCP
import platform
import sys
import datetime

# Initialize the FastMCP server
# "system-info" is the name of our server
mcp = FastMCP("system-info")

@mcp.tool()
def get_system_info() -> str:
    """Returns basic system information (OS, Python version)."""
    info = [
        f"System: {platform.system()} {platform.release()}",
        f"Python: {sys.version.split()[0]}",
        f"Time: {datetime.datetime.now().isoformat()}"
    ]
    return "\n".join(info)

@mcp.tool()
def echo(message: str) -> str:
    """Echoes back the message provided specifically for testing connection."""
    return f"Echo verified: {message}"

if __name__ == "__main__":
    # fastmcp.run() handles the stdio connection automatically
    mcp.run()
