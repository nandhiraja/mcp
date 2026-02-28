import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Config ────────────────────────────────────────────────────────────────────
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_FILE = os.path.join(DEMO_DIR, "demo_output.txt")

# ── Client ────────────────────────────────────────────────────────────────────

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,       # current python (venv-aware)
        args=["server.py"],
        env=os.environ.copy()         # inherit venv environment
    )

    print("🔌 Connecting to FileSystemAssistant MCP server...\n")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected!\n")

            # ── 1. List available tools ────────────────────────────────────
            tools = await session.list_tools()
            print("📋 Available Tools:")
            for t in tools.tools:
                print(f"   - {t.name}: {t.description}")
            print()




            # ── 2. Write a file ───────────────────────────────────────────
            print(f"✍️  Writing to: {DEMO_FILE}")
            result = await session.call_tool("write_file", arguments={
                "path": DEMO_FILE,
                "content": "Hello from MCP!\nLine 2: File access is working.\nLine 3: Done."
            })
            print(f"   Result: {result.content[0].text}\n")




            # ── 3. List files in the directory ────────────────────────────
            print(f"📁 Listing files in: {DEMO_DIR}")
            result = await session.call_tool("list_files", arguments={
                "directory": DEMO_DIR
            })
            files = result.content[0].text
            print(f"   Files: ")
            for i in result.content:
                print("   -",i.text)





            # ── 4. Read the file we just wrote ────────────────────────────
            print(f"📖 Reading back: {DEMO_FILE}")
            result = await session.call_tool("read_file", arguments={
                "path": DEMO_FILE
            })
            print(f"   Content:\n{result.content[0].text}\n")




            # ── 5. Edit (overwrite) the file ──────────────────────────────
            print(f"✏️  Editing file (overwrite)...")
            result = await session.call_tool("write_file", arguments={
                "path": DEMO_FILE,
                "content": "Updated content!\nEdit made via MCP write_file tool."
            })
            print(f"   Result: {result.content[0].text}\n")





            # ── 6. Read it again to confirm edit ─────────────────────────
            print(f"📖 Reading after edit:")
            result = await session.call_tool("read_file", arguments={
                "path": DEMO_FILE
            })
            print(f"   Content:\n{result.content[0].text}\n")

            print("✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
