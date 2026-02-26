from mcp.types import Resource, TextResourceContents, ReadResourceResult
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server import Server

# Logic for data retrieval
async def get_config_data():
    return "Mode: Development\nVersion: 1.0.0"

# Use a simple string-to-function   
RESOURCE_MAP = {
    "info://system/config": get_config_data,
}

def register_resources(server: Server):
    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        return [
            Resource(
                uri="info://system/config", 
                name="System Config", 
                mimeType="text/plain"
            ),
        ]

    
    @server.read_resource()
    async def handle_read_resource(uri: str) -> list[ReadResourceContents]:
        uri_str = str(uri)
        handler = RESOURCE_MAP.get(uri_str)
        
        if not handler:
            raise ValueError(f"Resource not found: {uri_str}")
        
        data = await handler()
        
        return [
            ReadResourceContents(
                content=data,
                mime_type="text/plain"
            )
        ]
    