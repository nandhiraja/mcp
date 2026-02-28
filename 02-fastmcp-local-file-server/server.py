from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP(name="FileSystemAssistant")



# ======================================================================
#                       tools
#=======================================================================

@mcp.tool()
def list_files(directory: str) -> list:
    """List all files in a directory."""
    try:
        print(os.listdir(directory))
        return os.listdir(directory)
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def read_file(path: str) -> str:
    """Read content of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(path, "w") as f:
            f.write(content)
        return "File written successfully"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()