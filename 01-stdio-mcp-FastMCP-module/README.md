# 01 — stdio MCP with FastMCP

> **Style: Personal Recall Notes**  
> Not a formal doc. Just enough to remember *why* each thing exists and *how* it works.

---

## What this project does

A simple MCP **server** that exposes two tools (`get_system_info`, `echo`),  
and a **client** that connects to it, lists tools, and calls them.  
Transport used: **stdio** (no HTTP, no ports — just processes talking through stdin/stdout).

---

## Concepts Used

---

### 1. `FastMCP` — The Server Container

```python
mcp = FastMCP("system-info")
```

**What it is:**  
A high-level wrapper around the raw MCP SDK. Think of it as your *entire server app in one object*.

**Why we need it:**  
MCP protocol is complex (JSON-RPC handshakes, capability negotiation, tool schemas…).  
`FastMCP` hides all that. You just register tools/resources, call `mcp.run()`, and it handles the rest.

**Simple mental model:**  
> "FastMCP is to MCP what Flask is to HTTP — a framework that does the heavy lifting."

**The name string `"system-info"`** → just the server's identity label. Clients see this name.

---

### 2. `@mcp.tool()` — Registering Tools

```python
@mcp.tool()
def get_system_info() -> str:
    """Returns basic system information."""
    ...
```

**What it is:**  
A decorator that *registers* your Python function as an MCP Tool.

**Why we need it:**  
LLMs can't run code — they only see text. Tools are the bridge.  
When you register a function as a tool:
- MCP auto-generates a **JSON schema** from your type hints
- It tells clients: "this function exists, here are its inputs/outputs"
- When a client calls it, MCP runs your function and returns the result

**How registration works internally:**  
`FastMCP` keeps an internal **registry** (a dict) of all tools.  
`@mcp.tool()` → adds your function + its schema to that registry.  
When a client sends `tools/list`, FastMCP reads from that registry to respond.

**Simple mental model:**  
> "The decorator is like pinning your function to a notice board that clients can read from."

**Docstring matters:**  
The `"""docstring"""` becomes the tool's `description` field — what the AI reads to decide when to call it.

---

### 3. `stdio` Transport — How Server & Client Talk

**What it is:**  
The communication channel. `stdio` = Standard Input / Standard Output.

**Why stdio (not HTTP)?**  
- No port conflicts, no firewall issues
- Perfect for local tools — client *spawns* the server as a subprocess
- The client writes JSON to the server's **stdin**, server writes JSON back to **stdout**

**What actually happens:**
```
Client Process              Server Process (subprocess)
    |                              |
    |--- JSON message --> stdin -->|
    |                              | (processes it)
    |<-- JSON response <-- stdout--|
```

**Simple mental model:**  
> "Two people passing notes through a pipe — no network needed."

---

### 4. `StdioServerParameters` — How Client Knows to Start the Server

```python
server_params = StdioServerParameters(
    command=sys.executable,   # which python
    args=["mcp_server.py"],   # which script
    env=os.environ.copy()     # environment (venv paths, etc.)
)
```

**What it is:**  
A config object that tells the client *how to launch the server process*.

**Why we need it:**  
The client doesn't expect the server to already be running.  
It spawns the server itself as a subprocess using this config.

**Key fields:**
| Field | Purpose |
|-------|---------|
| `command` | The executable (`python`) |
| `args` | Script to run |
| `env` | Pass venv paths so imports work correctly |

**Why `os.environ.copy()`?**  
If you're in a virtualenv, `sys.executable` points to the venv Python,  
but without `env`, the subprocess may not find installed packages.  
Copying the environment ensures the subprocess inherits your venv's `PATH` and `PYTHONPATH`.

---

### 5. `stdio_client` + `ClientSession` — The Client Side

```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

**`stdio_client`:**  
- Launches the server subprocess using `StdioServerParameters`
- Gives you back two streams: `read` (server's stdout) and `write` (server's stdin)

**`ClientSession`:**  
- Wraps those streams into a proper MCP session
- Handles the protocol handshake via `session.initialize()`
- Gives you clean methods: `list_tools()`, `call_tool()`, etc.

**Simple mental model:**  
> `stdio_client` = opens the pipe.  
> `ClientSession` = speaks MCP language through that pipe.

---

### 6. `async` / `await` / `asyncio` — Why Everything is Async

```python
async def run_client():
    ...
asyncio.run(run_client())
```

**Why async here?**  
MCP communication involves **waiting** — waiting for the server to process, waiting for I/O.  
`async/await` lets the program wait without freezing (non-blocking I/O).

**`asyncio.run()`** → entry point that runs an async function from regular (sync) Python code.

**Simple mental model:**  
> "Async = don't stand in line blocking everyone. Go do other things, come back when ready."

In MCP, almost everything is async because you're constantly sending/receiving messages.

---

### 7. `async with` — Context Managers for Cleanup

```python
async with stdio_client(...) as (read, write):
    async with ClientSession(...) as session:
```

**Why `with`?**  
These are **async context managers** — they automatically clean up when done:
- `stdio_client` → kills the subprocess on exit
- `ClientSession` → closes the session cleanly

Without `with`, you'd have to manually close connections (and risk leaks if something errors).

---

## Flow Summary

```
python client_server.py
        │
        ▼
StdioServerParameters  ──► spawns ──► mcp_server.py (subprocess)
        │
        ▼
stdio_client  ──► opens stdin/stdout pipe to subprocess
        │
        ▼
ClientSession.initialize()  ──► MCP handshake
        │
        ▼
session.list_tools()   ──► FastMCP reads its registry → returns tool list
        │
        ▼
session.call_tool("get_system_info")  ──► FastMCP runs the function → returns result
```

---

## Run It

```bash
python client_server.py
```

> Server is launched automatically by the client. No need to start it separately.
