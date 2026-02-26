import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_test():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )

    print("--- 🚀 Connecting to MCP Server ---")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Fetch all capabilities once
            tools_resp = await session.list_tools()
            resources_resp = await session.list_resources()
            prompts_resp = await session.list_prompts()

            while True:
                print("\n" + "="*30)
                print("MAIN MENU:")
                print("1. Call a Tool")
                print("2. Read a Resource")
                print("3. Get a Prompt")
                print("4. Exit")
                choice = input("Select an option (1-4): ")

                if choice == "1":
                    # --- TOOL LOGIC ---
                    print("\nAvailable Tools:")
                    for t in tools_resp.tools:
                        print(f" - {t.name}: {t.description}")
                    
                    target = input("\nEnter tool name: ")
                    tool = next((t for t in tools_resp.tools if t.name == target), None)
                    
                    if tool:
                        args = {}
                        properties = tool.inputSchema.get("properties", {})
                        if properties:
                            print(f"Tool requires: {list(properties.keys())}")
                            for key in properties:
                                val = input(f"  Enter value for '{key}': ")
                                # Simple type conversion
                                if properties[key].get("type") == "integer":
                                    args[key] = int(val)
                                else:
                                    args[key] = val
                        
                        print(f"Calling {target}...")
                        result = await session.call_tool(target, arguments=args)
                        for content in result.content:
                            print(f"Output: {content.text}")
                    else:
                        print("Invalid tool name.")

                elif choice == "2":
                    # --- RESOURCE LOGIC ---
                    print("\nAvailable Resources:")
                    for r in resources_resp.resources:
                        print(f" - {r.uri} ({r.name})")
                    
                    uri = input("\nEnter resource URI: ")
                    print(f"Reading {uri}...")
                    try:
                        # Note: session.read_resource returns a ReadResourceResult
                        result = await session.read_resource(uri)
                        for content in result.contents:
                            print(f"Content:\n{content.text}")
                    except Exception as e:
                        print(f"Error: {e}")

                elif choice == "3":
                    # --- PROMPT LOGIC ---
                    print("\nAvailable Prompts:")
                    for p in prompts_resp.prompts:
                        print(f" - {p.name}: {p.description}")
                    
                    p_name = input("\nEnter prompt name: ")
                    print(f"Fetching prompt {p_name}...")
                    try:
                        result = await session.get_prompt(p_name, arguments={})
                        for msg in result.messages:
                            print(f"[{msg.role.upper()}]: {msg.content.text}")
                    except Exception as e:
                        print(f"Error: {e}")

                elif choice == "4" or not choice:
                    break

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\nShutdown.")
    except Exception as e:
        print(f"\nCritical Error: {e}")

