from mcp.server.fastmcp import FastMCP, Context
import sqlite3
from typing import List, Dict, Any

# Initialize FastMCP server
mcp = FastMCP("sqlite-todo")

DB_PATH = "todos.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initialize the database with the todos table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
initialize_db()

@mcp.resource("todo://list")
def list_todos() -> str:
    """List all todos in the database as a JSON string."""
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos').fetchall()
    conn.close()
    
    todo_list = [dict(todo) for todo in todos]
    return str(todo_list)

@mcp.tool()
def add_todo(title: str) -> str:
    """Add a new todo item.
    
    Args:
        title: The title of the todo item.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todos (title) VALUES (?)', (title,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return f"Added todo with ID {new_id}: '{title}'"

@mcp.tool()
def complete_todo(todo_id: int) -> str:
    """Mark a todo item as completed.
    
    Args:
        todo_id: The ID of the todo item to complete.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
    if cursor.rowcount == 0:
        conn.close()
        return f"Todo with ID {todo_id} not found."
    conn.commit()
    conn.close()
    return f"Marked todo {todo_id} as completed."

@mcp.tool()
def delete_todo(todo_id: int) -> str:
    """Delete a todo item.
    
    Args:
        todo_id: The ID of the todo item to delete.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    if cursor.rowcount == 0:
        conn.close()
        return f"Todo with ID {todo_id} not found."
    conn.commit()
    conn.close()
    return f"Deleted todo {todo_id}."

if __name__ == "__main__":
    mcp.run()
