from langchain_mcp_adapters.client import MultiServerMCPClient
import os

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
                    "GOOGLE_OAUTH_CREDENTIALS": os.path.join(os.path.dirname(__file__), "..", "agent", "credentials.json")
                }
            }
        }
        
        self.client = MultiServerMCPClient(config)
        self.tools = await self.client.get_tools()
        return self.tools

    def get_tool_by_name(self, name: str):
        """Devuelve una herramienta específica filtrando por nombre"""
        return next((t for t in self.tools if name in t.name), None)

    def get_tools_by_namespace(self, namespace: str):
        """Devuelve herramientas filtrando por namespace"""
        namespace_map = {
            "google_calendar": ["list-events", "get-event", "create-event", "update-event", "delete-event", "calendar", "event", "list_events"],
            "tavily": ["tavily", "search"],
            "pdf": ["pdf", "markdown"]
        }
        keywords = namespace_map.get(namespace, [namespace])
        return [t for t in self.tools if any(kw.lower() in t.name.lower() for kw in keywords)]

    def get_tools(self):
        """Devuelve todas las herramientas"""
        return self.tools

    async def disconnect(self):
        """Cierra las conexiones de forma limpia"""
        if self.client:
            await self.client.close()