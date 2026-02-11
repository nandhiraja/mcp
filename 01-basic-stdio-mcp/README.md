# 01 Basic Stdio MCP

This is the first project in the MCP learning series. It demonstrates a simple MCP server that communicates over `stdio`.

## Features

- **Protocol**: Standard Input/Output (stdio) communication.
- **Tools**:
    - `get_system_info()`: Returns basic system information (OS, Python version).
    - `echo(message)`: Echoes back a message for testing.

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

The server is designed to be run as a subprocess by an MCP client (like `client.py` or Claude Desktop).

```bash
python server.py
```

### Testing with Client

You can run the included client script to test the tools:

```bash
python client.py
```
