# 02 — FastMCP Local File Server

> **Style: Personal Recall Notes**  
> First project where MCP tools touch the **real filesystem**.  
> Concepts: file I/O with `open()`, `os.listdir()`, error handling as return values, `os.path` helpers.

---

## What this project does

A FastMCP server that exposes 3 tools to **read, list, and write files** on the local machine.  
A scripted client exercises all three tools in sequence — write → list → read → edit → read again.

**Files:**
```
02-fastmcp-local-file-server/
├── server.py          # FastMCP server with 3 filesystem tools
├── client.py          # Scripted demo client
└── demo_output.txt    # Created automatically when client runs
```

---

## Concepts Used

---

### 1. Filesystem Tools — What They Do

| Tool | Args | What it does | Python underneath |
|---|---|---|---|
| `list_files(directory)` | path string | List files in a folder | `os.listdir(directory)` |
| `read_file(path)` | path string | Read file contents | `open(path, "r").read()` |
| `write_file(path, content)` | path + content | Create or overwrite a file | `open(path, "w").write()` |

**`write_file` = create OR overwrite:**  
Opening with `"w"` always starts fresh. If the file doesn't exist → created. If it does → overwritten.  
There's no append here — every call replaces the entire file.

---

### 2. `try / except` as Return Values — Error Handling Pattern

```python
@mcp.tool()
def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"
```

**Why return the error as a string instead of raising?**  
If you `raise` inside an MCP tool, the exception propagates up the MCP protocol stack  
and the client receives an error response (potentially crashing it).

By catching and returning `"Error: ..."` as a normal string:
- The tool never fails from the protocol's perspective
- The client still gets a useful message
- The AI can read the error text and respond intelligently

**Simple mental model:**  
> MCP tools should never crash — wrap everything in try/except and return the error as text.

---

### 3. `os.listdir(directory)` — Listing Files

```python
return os.listdir(directory)
```

**What it returns:** A plain Python `list` of filenames (strings) — no full paths, just names.

```python
# e.g.:
["server.py", "client.py", "demo_output.txt"]
```

**Note:** It lists *everything* — files AND subdirectories mixed together.  
To tell them apart you'd use `os.path.isfile()` / `os.path.isdir()`, but here we keep it simple.

**What if path is wrong?** → `os.listdir` raises `FileNotFoundError` → caught by `except` → returned as error string.

---

### 4. `open(path, "r")` and `open(path, "w")` — File Modes

| Mode | Meaning | Creates file? | Overwrites? |
|---|---|---|---|
| `"r"` | Read | No (error if missing) | — |
| `"w"` | Write | Yes | Yes (replaces all) |
| `"a"` | Append | Yes | No (adds to end) |

**Why `with open(...) as f:`?**  
`with` is a context manager — it automatically closes the file when the block exits,  
even if an error happens inside. Without it, you could leave file handles open.

**Simple mental model:**  
> `with open(...)` = "borrow the file, work with it, return it when done — guaranteed."

---

### 5. `os.path` Helpers in the Client

```python
DEMO_DIR  = os.path.dirname(os.path.abspath(__file__))
DEMO_FILE = os.path.join(DEMO_DIR, "demo_output.txt")
```

**`__file__`** → the path of the currently running script.  
**`os.path.abspath(__file__)`** → turns it into a full absolute path.  
**`os.path.dirname(...)`** → strips the filename, leaving just the folder.  
**`os.path.join(dir, "file")`** → combines folder + filename safely (handles `\` vs `/` per OS).

**Why do this instead of hardcoding `"C:\\Users\\...\\demo.txt"`?**  
`os.path.join` + `__file__` makes paths work on any machine, regardless of where the project lives.

---

### 6. `result.content[0].text` — Reading Tool Output

```python
result = await session.call_tool("write_file", arguments={...})
print(result.content[0].text)
```

**Why `[0]`?**  
Tool results return a list of content blocks (could be text, images, etc.).  
Most text tools return exactly one block → `[0]` is always the first (and only) one.  
`.text` extracts the string from that block.

---

### 7. Server Has No State — Each Tool Call is Independent

Unlike the SQLite todo server (which had a persistent DB), this server has **no state**.  
Every tool call directly touches the filesystem — nothing is stored in memory.

**What this means:**
- Restart the server → no data lost (files are on disk)
- Multiple clients could theoretically call the same server (files are shared on disk)
- The server itself is completely stateless — just a thin Python wrapper over file I/O

---

## Flow Summary

```
python client.py
        │
        ▼
StdioServerParameters ──► spawns ──► server.py
server.py: FastMCP("FileSystemAssistant") starts, registers 3 tools
        │
session.initialize() → handshake complete
        │
call_tool("write_file",  {path, content})  →  open(path, "w") → writes file
call_tool("list_files",  {directory})      →  os.listdir()    → returns file list
call_tool("read_file",   {path})           →  open(path, "r") → returns content
call_tool("write_file",  {path, new})      →  open(path, "w") → overwrites file
call_tool("read_file",   {path})           →  open(path, "r") → confirms edit
        │
        ▼
demo_output.txt exists on disk ✅
```

---

## Run It

```bash
python client.py
```

> `demo_output.txt` is created in the same folder during the run.  
> Calling `write_file` again replaces its contents entirely (mode `"w"`).
