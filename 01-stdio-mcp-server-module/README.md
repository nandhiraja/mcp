# 01 — stdio MCP with raw `Server` SDK

> **Style: Personal Recall Notes**  
> This is the *manual* version — no FastMCP shortcut. You register everything yourself.  
> Key difference from the FastMCP module: you control every layer.

---

## What this project does

A structured MCP server built with the **low-level `Server` SDK** (not FastMCP).  
Exposes **Tools**, **Resources**, and **Prompts** — all three MCP capability types.  
Client is an interactive terminal menu that lets you call any capability manually.

**Folder layout:**
```
01-stdio-mcp-server-module/
│
├── mcp_server.py          # Entry point — wires everything together & runs
└── app/
    ├── server.py          # Creates the bare Server instance
    ├── tools.py           # Tool functions + registration
    ├── resource.py        # Resource functions + registration
    └── prompt.py          # Prompt functions + registration
```

---

## Concepts Used

---

### 1. `Server` (raw SDK) vs `FastMCP`

```python
from mcp.server import Server
server = Server(name="local-test-mcp-server")
```

**What it is:**  
The bare-metal MCP server class. No magic, no auto-schema generation.

**Why use it instead of FastMCP?**  
FastMCP auto-generates schemas from type hints. `Server` makes you do it manually.  
That means you understand *exactly* what JSON goes over the wire.

**Comparison:**
| | `FastMCP` | `Server` (raw) |
|---|---|---|
| Schema generation | Automatic from type hints | You write JSON schema by hand |
| Registration | `@mcp.tool()` decorator | `@server.list_tools()` + `@server.call_tool()` |
| Learning value | Fast to use | Teaches the actual protocol |

**Simple mental model:**  
> FastMCP = car with automatic transmission.  
> Server (raw) = car with manual — you understand what gears do.

---

### 2. App Factory Pattern — `create_app()`

```python
def create_app():
    app = create_server()
    register_tools(app)
    register_prompts(app)
    register_resources(app)
    return app
```

**What it is:**  
A function that builds the complete server object by assembling all its parts.

**Why not just put everything in one file?**  
- Separation of concerns — tools, prompts, resources are independent
- Each module (`tools.py`, `resource.py`, `prompt.py`) owns its own logic
- The factory just *wires* them together

**Simple mental model:**  
> Think of it like assembling a car: engine, wheels, and seats are built separately,  
> then the factory assembles the final vehicle.

---

### 3. Two-Decorator Pattern — `list` + `call`

Every capability in raw `Server` needs **two decorators**: one to *list*, one to *execute*.

#### For Tools (`tools.py`):
```python
@server.list_tools()
async def handle_tool_list() -> list[Tool]:
    return [Tool(name="add_numbers", description="...", inputSchema={...})]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    tool_handler = TOOL_MAP.get(name)
    return await tool_handler(arguments or {})
```

**Why two?**  
- `list_tools` → answers "what tools exist?" (client calls this to discover)  
- `call_tool` → answers "run this tool now" (client calls this to execute)

These are two separate MCP protocol messages. The SDK needs a handler for each.

Same pattern for Resources and Prompts:
| Capability | List decorator | Execute decorator |
|---|---|---|
| Tool | `@server.list_tools()` | `@server.call_tool()` |
| Resource | `@server.list_resources()` | `@server.read_resource()` |
| Prompt | `@server.list_prompts()` | `@server.get_prompt()` |

---

### 4. `TOOL_MAP` / `RESOURCE_MAP` / `PROMPT_MAP` — The Dispatch Dictionary

```python
TOOL_MAP = {
    "add_numbers": add_numbers,
    "multiply_numbers": mul_numbers,
    "get_status": sys_config
}
```

**What it is:**  
A plain Python `dict` that maps a string name → the actual function to call.

**Why we need it:**  
The `@server.call_tool()` handler receives just the string name from the client.  
You need a way to route that name to the right Python function.

Without a map, you'd write ugly `if/elif` chains:
```python
# Without map (bad):
if name == "add_numbers":
    return await add_numbers(args)
elif name == "multiply_numbers":
    return await mul_numbers(args)
# ... forever

# With map (clean):
tool_handler = TOOL_MAP.get(name)
return await tool_handler(args)
```

**Simple mental model:**  
> The map is a phone directory — you look up the name, get the number (function), and call it.

**What happens if name is wrong?**  
`TOOL_MAP.get(name)` returns `None` → you raise `ValueError("Tool not found")`.

---

### 5. `Tool(name, description, inputSchema)` — Manual Schema

```python
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
)
```

**What it is:**  
A Pydantic model (from `mcp.types`) that describes a tool to the outside world.

**Why write `inputSchema` manually?**  
This is raw JSON Schema — what FastMCP generates for you automatically from type hints.  
Here you write it yourself so the client knows what arguments your tool expects.

**Fields:**
| Field | Purpose |
|---|---|
| `name` | Identifier used to call the tool |
| `description` | What the AI/client reads to understand the tool |
| `inputSchema` | JSON Schema defining the arguments |

---

### 6. Resources — "Read-only Data the AI Can Access"

```python
Resource(uri="info://system/config", name="System Config", mimeType="text/plain")
```

**What it is:**  
Resources are like **files or data endpoints** the AI can read.  
They have a URI (like a URL), not a function name.

**How the URI routing works:**
```python
RESOURCE_MAP = {
    "info://system/config": get_config_data,
}

handler = RESOURCE_MAP.get(uri_str)  # same dispatch dict pattern
```

**Why a custom URI scheme (`info://`)?**  
MCP resources use URIs to identify data. You can invent any scheme (`info://`, `db://`, `file://`…).  
It's just an identifier string — the map routes it to your actual function.

**Simple mental model:**  
> Resource = a page you can GET (read-only). Tool = an action you can POST (do something).

---

### 7. Prompts — "Reusable System Instructions"

```python
Prompt(name="math_expert", description="Act like a math professor")

# Returns:
PromptMessage(role="user", content=TextContent(type="text", text="You are a math professor."))
```

**What it is:**  
Prompts are **pre-written instructions** the client can fetch and inject into an AI conversation.  
They are not executed like tools — they just return text messages.

**Why wrap in `GetPromptResult`?**
```python
return GetPromptResult(messages=messages)
```
The `@server.get_prompt()` handler **must** return a `GetPromptResult` object.  
Returning a raw list won't work — the SDK validates the response type.

**Simple mental model:**  
> Prompt = a saved template. "Give me the math expert template" → server returns the text.

---

### 8. `stdio_server()` — Low-level Transport

```python
async with stdio_server() as (read_stream, write_stream):
    await app.run(read_stream, write_stream, app.create_initialization_options())
```

**What it is:**  
The low-level equivalent of FastMCP's `mcp.run()`.  
It opens the stdin/stdout streams and you pass them directly to `app.run()`.

**Why explicit streams here?**  
FastMCP hides this. Here you see that the server is just reading from stdin and writing to stdout — raw stream I/O.

**`create_initialization_options()`** → generates the MCP handshake config (protocol version, capabilities) that gets sent to the client on first connect.

---

### 9. Error Logging to File

```python
except Exception:
    with open("server_error.log", "w") as f:
        f.write(traceback.format_exc())
    sys.exit(1)
```

**Why log to a file (not print)?**  
The server's stdout is the communication channel with the client.  
Any stray `print()` or traceback on stdout would corrupt the JSON protocol stream.  
So errors go to a **file** (`server_error.log`) instead.

**Simple mental model:**  
> stdout = the pipe between client and server. Never pollute the pipe with debug text.

---

## Flow Summary

```
python client_server.py
        │
        ▼
StdioServerParameters ──► spawns ──► mcp_server.py (subprocess)
        │
        ▼
mcp_server.py: create_app()
  ├── create_server()           → bare Server instance
  ├── register_tools(app)       → attaches list_tools + call_tool handlers
  ├── register_prompts(app)     → attaches list_prompts + get_prompt handlers
  └── register_resources(app)  → attaches list_resources + read_resource handlers
        │
        ▼
stdio_server() opens streams → app.run() starts listening
        │
        ▼
Client: session.initialize() → handshake
Client: list_tools() / list_resources() / list_prompts() → reads registered handlers
Client: call_tool("add_numbers", {a:2, b:3})
        │
        ▼
handle_call_tool("add_numbers", {a:2, b:3})
  └── TOOL_MAP.get("add_numbers") → add_numbers() → returns TextContent("5")
```

---

## Run It

```bash
python client_server.py
```

> Interactive menu will appear. Choose Tool / Resource / Prompt to test each capability.
