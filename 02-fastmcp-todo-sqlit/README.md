# 02 — FastMCP Todo with SQLite

> **Style: Personal Recall Notes**  
> First project that connects MCP to a real database.  
> Key additions over the previous modules: **`@mcp.resource()`**, **SQLite**, **`conn.row_factory`**, **`cursor.lastrowid`**.

---

## What this project does

A FastMCP server that manages a **persistent todo list** stored in SQLite.  
Exposes **3 Tools** (add, complete, delete) and **1 Resource** (read all todos).  
Client is a scripted flow that calls each tool and reads the resource in sequence.

**Files:**
```
02-fastmcp-todo-sqlit/
├── server.py     # FastMCP server + SQLite logic
├── client.py     # Scripted client that exercises the server
└── todos.db      # SQLite database file (auto-created on first run)
```

---

## Concepts Used

---

### 1. `@mcp.resource("todo://list")` — Resources with FastMCP

```python
@mcp.resource("todo://list")
def list_todos() -> str:
    ...
    return str(todo_list)
```

**What it is:**  
A FastMCP decorator that registers a function as an MCP **Resource** — identified by a URI string.

**How it differs from `@mcp.tool()`:**

| | `@mcp.tool()` | `@mcp.resource(uri)` |
|---|---|---|
| Purpose | Do something (action) | Read something (data) |
| Client call | `session.call_tool(name, args)` | `session.read_resource(uri)` |
| Analogy | POST request | GET request |
| Has arguments | Yes (from type hints) | Typically no |

**Why use a resource instead of a tool for listing?**  
Resources signal to the AI: "this is data you can read, not an action."  
Tools signal: "this changes something."  
Semantically correct → AI makes better decisions about when to call what.

**The URI `"todo://list"` — custom scheme:**  
`todo://` is invented. MCP just needs any valid URI string.  
The scheme you pick communicates intent: `todo://` = this is todo-related data.

---

### 2. SQLite — Persistent Storage

```python
import sqlite3
DB_PATH = "todos.db"
```

**Why SQLite for MCP?**  
- Zero setup — a single `.db` file, no server needed
- Data survives between client runs (unlike an in-memory list)
- `sqlite3` is in Python's standard library — no install needed

**Basic pattern used:**
```
connect → execute query → commit → close
```

---

### 3. `get_db_connection()` — Connection Factory

```python
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

**What it is:**  
A helper function that creates and returns a fresh database connection.

**Why a function (not a global connection)?**  
SQLite connections are not thread-safe for sharing.  
Creating a new connection per operation → simple and safe.

**`conn.row_factory = sqlite3.Row` — Why?**  
By default, SQLite returns rows as plain tuples: `(1, "Buy milk", 0)`.  
With `row_factory = sqlite3.Row`, rows behave like dicts: `row["title"]`, `row["completed"]`.  
Then `dict(row)` converts it cleanly to a Python dict for easy use.

**Simple mental model:**  
> `row_factory` = teaches SQLite to speak dict instead of tuple.

---

### 4. `initialize_db()` — Auto Schema Creation

```python
def initialize_db():
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
```

**Why `CREATE TABLE IF NOT EXISTS`?**  
This runs every time the server starts.  
`IF NOT EXISTS` means: "only create if it doesn't already exist" — safe to call repeatedly.  
On first run → creates the table. Every run after → does nothing.

**`AUTOINCREMENT`:**  
SQLite auto-assigns an incrementing integer `id` to each row.  
You don't pass an `id` when inserting — the database handles it.

---

### 5. `cursor.lastrowid` — Getting the ID After Insert

```python
cursor = conn.cursor()
cursor.execute('INSERT INTO todos (title) VALUES (?)', (title,))
conn.commit()
new_id = cursor.lastrowid
```

**What it is:**  
After an `INSERT`, `cursor.lastrowid` gives you the auto-generated `id` of the row just inserted.

**Why we need it:**  
You didn't specify the `id` (AUTOINCREMENT handles it).  
To tell the user "Added todo with ID 3", you need to ask the cursor what ID was assigned.

**Why use `cursor` explicitly (not `conn.execute`)?**  
`conn.execute()` is a shortcut but returns a cursor anyway.  
Using `conn.cursor()` + `cursor.execute()` separates creating the cursor from using it,  
so you can read `.lastrowid` after the insert.

---

### 6. `cursor.rowcount` — Did the Update/Delete Actually Work?

```python
cursor.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
if cursor.rowcount == 0:
    return f"Todo with ID {todo_id} not found."
```

**What it is:**  
After `UPDATE` or `DELETE`, `cursor.rowcount` tells you how many rows were affected.

**Why check it?**  
If the ID doesn't exist, SQLite runs the query without error — it just affects 0 rows.  
Without checking `rowcount`, you'd silently return "success" even when nothing changed.

**Simple mental model:**  
> `rowcount == 0` means "the WHERE clause matched nothing."

---

### 7. Parameterized Queries — `?` Placeholders

```python
cursor.execute('INSERT INTO todos (title) VALUES (?)', (title,))
cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
```

**What it is:**  
`?` is a placeholder. The real value is passed as the second argument (a tuple).

**Why not f-strings?**
```python
# NEVER do this:
cursor.execute(f"DELETE FROM todos WHERE id = {todo_id}")
```
Using f-strings opens SQL Injection vulnerabilities.  
`?` placeholders → SQLite safely escapes the value before inserting into the query.

**Simple mental model:**  
> `?` = "fill this in safely." Always use it, never string-format SQL.

---

### 8. Tools vs Resource — Side by Side in This Project

```
add_todo("Buy milk")     → @mcp.tool()   → INSERT into DB → returns "Added todo ID 1"
complete_todo(1)         → @mcp.tool()   → UPDATE in DB   → returns "Marked todo 1 done"
delete_todo(1)           → @mcp.tool()   → DELETE from DB → returns "Deleted todo 1"

list all todos           → @mcp.resource("todo://list") → SELECT * → returns string of list
```

**Key insight:**  
Tools mutate state (write). Resources read state (read).  
This separation keeps MCP semantics clean — important when an AI decides what to call.

---

### 9. Reading a Resource from the Client

```python
resource_content = await session.read_resource("todo://list")
print(resource_content.contents[0].text)
```

**Note:** It's `.contents` (plural) — a list of content blocks.  
Even if only one block is returned, you access it with `[0]`.  
Compare with `call_tool` which gives `.content` (also a list, same pattern).

---

## Flow Summary

```
python client.py
        │
        ▼
StdioServerParameters ──► spawns ──► server.py
        │
        ▼
server.py startup:
  initialize_db()  →  CREATE TABLE IF NOT EXISTS todos (...)
  FastMCP registers: 3 tools + 1 resource
        │
        ▼
session.initialize()  →  handshake
        │
session.call_tool("add_todo", {"title": "Buy milk"})
  └── INSERT INTO todos (title) VALUES ("Buy milk")
  └── returns cursor.lastrowid → "Added todo with ID 1"
        │
session.read_resource("todo://list")
  └── SELECT * FROM todos → dict(row) for each → returns string
        │
session.call_tool("complete_todo", {"todo_id": 1})
  └── UPDATE todos SET completed = 1 WHERE id = 1
  └── cursor.rowcount check → success
        │
session.call_tool("delete_todo", {"todo_id": 1})
  └── DELETE FROM todos WHERE id = 1
  └── cursor.rowcount check → success
```

---

## Run It

```bash
python client.py
```

> `todos.db` is created automatically on first run. Each run adds more data to the same file.  
> Delete `todos.db` to start fresh.
