# 02 SQLite Todo MCP

This project advances your MCP skills by introducing **Resources** and **State Management**.

## Core Concepts Learned

### 1. `mcp.resource()` - "The Eyes"
Resources are **read-only data** that the AI can look at.
- **What it does**: `@mcp.resource("todo://list")` creates a direct link to data. Unlike a tool, which requires the AI to *decide* to call it, a resource is often provided to the AI as context automatically or fetched when needed without side effects (changing data).
- **Internal Working**: The schema `todo://list` acts like a "local URL" for your AI. When the AI "reads" this resource, your function `list_todos()` runs and returns the data.
- **Why use it**: Use resources for data that changes often or is large, where you want the AI to just "see" it. For example: logs, list of files, or in this case, the current list of todos.

### 2. State Management (SQLite)
In Project 01, the server forgot everything when it restarted. Here, we use a database (`todos.db`).
- **Internal Working**: We use Python's built-in `sqlite3` module. The `tools` (add/complete/delete) execute SQL queries (`INSERT`, `UPDATE`, `DELETE`) to modify the database file. The `resource` executes a `SELECT` query to read it.
- **Future Application**: In real-world apps, this "State" could be a Postgres database, a File System, or a Cloud API. The logic remains the same: **Tools modify state, Resources read state.**

## Features

- **Resources** (Passive Data):
    - `todo://list` -> Returns the full JSON list of todos.
- **Tools** (Active Capabilities):
    - `add_todo(title)` -> Adds a row to the DB.
    - `complete_todo(id)` -> Updates a row in the DB.
    - `delete_todo(id)` -> Removes a row from the DB.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the server directly (for testing/development):
    ```bash
    python server.py
    ```

## Testing with Client

Run the included client script. It will sequentially call the tools and read the resources to demonstrate the flow.

```bash
python client.py
```
