# MCP — Model Context Protocol

> Quick notes on how MCP works, why it exists, and what you need to know.

---

## What is MCP?

**MCP (Model Context Protocol)** is an open standard that lets AI models (like LLMs) communicate with external tools, data sources, and services in a structured, predictable way.

Think of it as a **USB-C port for AI** — a single, unified interface so any AI host can talk to any MCP-compatible server without custom glue code.

---

## Why MCP?

Without MCP every AI integration is custom-built:

```
AI App  ──── custom code ────  Tool A
AI App  ──── custom code ────  Tool B
AI App  ──── custom code ────  Tool C
```

With MCP you write the integration once:

```
AI App  ──── MCP ────  Server A (tools, resources, prompts)
              │
              └────  Server B (tools, resources, prompts)
```

---

## Core Architecture

```
┌──────────────────────────────────────────────────────────┐
│                        MCP HOST                          │
│  (Claude Desktop, VS Code, your custom AI app, etc.)     │
│                                                          │
│   ┌─────────────┐        ┌─────────────┐                 │
│   │ MCP Client  │◄──────►│ MCP Client  │  (one per       │
│   └──────┬──────┘        └──────┬──────┘   server)       │
└──────────┼────────────────────┼───────────────────────────┘
           │  MCP Protocol      │  MCP Protocol
           ▼                    ▼
   ┌───────────────┐    ┌───────────────┐
   │  MCP Server A │    │  MCP Server B │
   │  (your code)  │    │  (your code)  │
   └───────────────┘    └───────────────┘
```

| Layer | Role |
|-------|------|
| **Host** | The AI application (Claude, a chatbot, an agent) |
| **Client** | Lives inside the host; manages one connection to one server |
| **Server** | Your code that exposes tools, resources, and prompts |

---

## The Three Primitives

Everything a server can expose falls into one of three buckets:

| Primitive | What it is | Example |
|-----------|-----------|---------|
| **Tool** | A function the model can *call* | `search_web()`, `run_query()` |
| **Resource** | Data the model can *read* | A file, a DB row, an API response |
| **Prompt** | A reusable prompt template | A system prompt with parameters |

---

## Transport Layers

MCP is transport-agnostic. Two transports are standard:

| Transport | When to use |
|-----------|-------------|
| **stdio** | Local processes; the host spawns the server as a subprocess. Simple, no networking needed. |
| **HTTP + SSE** | Remote servers; server runs independently, clients connect over the network. |

---

## Request / Response Flow

```
Host asks model → model wants a tool → Client sends JSON-RPC request
                                              │
                                              ▼
                                        MCP Server
                                         executes tool
                                              │
                                              ▼
                                    JSON-RPC response
                                              │
                                              ▼
                               Client returns result to Host
                               Host passes result back to model
```

All messages are **JSON-RPC 2.0**.

---

## Important Notes

- **MCP is stateful by design** — each client-server pair maintains a persistent session (especially important for stdio).
- **Capability negotiation happens at startup** — the client and server exchange what they support during the `initialize` handshake.
- **Tools are model-controlled** — the model decides *when* and *whether* to call a tool; the host decides *which* tools to expose.
- **Resources are application-controlled** — the host/client decides which resources to attach to context, not the model.
- **Security is your responsibility** — MCP servers can execute code and access data. Always validate inputs and restrict permissions.
- **FastMCP** is a high-level Python library that simplifies building MCP servers with decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`).

---

## Quick Cheat-Sheet

```python
# Minimal FastMCP server (stdio)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run()  # uses stdio by default
```

```python
# Switch to HTTP transport
mcp.run(transport="sse")   # runs on http://localhost:8000/sse
```

---

## Key Vocabulary

| Term | Meaning |
|------|---------|
| **Host** | App that embeds an LLM and uses MCP |
| **Client** | Protocol layer inside the host |
| **Server** | Your MCP-compliant service |
| **Tool** | Callable function exposed to the model |
| **Resource** | Readable data exposed to the model |
| **Prompt** | Reusable prompt template |
| **stdio** | Local subprocess transport |
| **SSE** | Server-Sent Events HTTP transport |
| **JSON-RPC 2.0** | Wire format for all MCP messages |

---

> **Spec & Docs:** [modelcontextprotocol.io](https://modelcontextprotocol.io) · [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
