from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPServer:
    def __init__(self):
        self.client = None
        self.tools = []

    async def connect(self):
        """Inicializa las conexiones con todos los servidores MCP"""
        config = {
            "tavily": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "tavily-mcp@latest"],
                "env": {"TAVILY_API_KEY": "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"}
            },
            "pdf-generator": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "markdown2pdf-mcp"] 
            },
            "google-calendar": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@cocal/google-calendar-mcp"],
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": "/home/inta@informatica.edu/Escritorio/PRO/Proyecto-final-ia/backend/agent/credentials.json"
                }
            }
        }
        
        self.client = MultiServerMCPClient(config)
        self.tools = await self.client.get_tools()
        return self.tools

    def get_tool_by_name(self, name: str):
        """Devuelve una herramienta específica filtrando por nombre"""
        return next((t for t in self.tools if name in t.name), None)

    async def disconnect(self):
        """Cierra las conexiones de forma limpia"""
        if self.client:
            await self.client.close()