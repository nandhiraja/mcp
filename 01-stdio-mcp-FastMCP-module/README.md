# 01 Basic Stdio MCP

This is the first project in the MCP learning series. It demonstrates the most fundamental building block of an MCP server: **Tools** communicated over **Common Input/Output (stdio)**.

## Core Concepts Learned
Pydantic Validation: The MCP Python SDK uses Pydantic to enforce the protocol. The Tool object requires name, description, and inputSchema
### 1. `FastMCP`
We use `FastMCP("system-info")` to create our server application. Think of this as the "container" for all your AI capabilities. It handles all the complex networking protocol details for you, so you can focus on writing Python functions.

### 2. `mcp.tool()` - "The Actions"
Tools are **functions that the AI can call**. They are the "hands" of the AI.

- **What it does**: When you decorate a Python function with `@mcp.tool()`, you are telling the MCP server: "Hey, tell the AI that this function exists, what arguments it needs, and what it returns."
- **Why we use it**: LLMs (Large Language Models) cannot run code directly on your computer. They can only output text. An MCP Tool bridges this gap. The AI asks to run "get_system_info", the MCP server runs your Python code, and sends the result back to the AI.
- **In this project**:
    - `get_system_info()`: A tool that fetches data from your OS.
    - `echo(message)`: A tool that helps verify the loop is working.

### 3. `stdio` - "The Phone Line"
This server speaks standard MCP protocol over the command line (Standard Input/Output).
- **Internal Working**: When you run this script, it doesn't open a website. Instead, it listens for JSON messages typed into the terminal console (stdin) and prints JSON messages back (stdout). This is how the AI "talks" to your code.

## Setup

1.  Navigate to the directory:
    ```bash
    cd 01-basic-stdio-mcp
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Server

Since this uses `stdio`, running it directly (`python server.py`) will just make it sit there waiting for input. It is meant to be run by a **Client**.

### Testing with Client

We provided a `client.py` to act as the AI. Run it to see the magic happen:

```bash
python client.py
```
