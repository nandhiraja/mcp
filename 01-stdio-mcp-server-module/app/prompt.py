from mcp.types import Prompt, PromptMessage, TextContent, GetPromptResult
from mcp.server import Server

async def expert_mathematician_prompt(args: dict):
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text="You are a math professor.")
        )
    ]

PROMPT_MAP = {
    "math_expert": expert_mathematician_prompt,
}

def register_prompts(server: Server):
    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        return [
            Prompt(name="math_expert", description="Act like a math professor"),
        ]

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        handler = PROMPT_MAP.get(name)
        if not handler:
            raise ValueError(f"Prompt not found: {name}")
        
        messages = await handler(arguments or {})
        # You MUST wrap the list of messages in a GetPromptResult:
        return GetPromptResult(messages=messages)