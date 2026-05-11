from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from backend.agent.prompts import ROUTER_PROMPT
from backend.agent.rag_agent import tool_equipos, tool_presupuestos, tool_sonido
from backend.tools.send_email import send_email_tool
from backend.tools.generate_pdf import generar_pdf_presupuesto
import aiosqlite
import os

SQLITE_PATH = os.path.join("database/memoria_agente.sqlite")

os.makedirs("database", exist_ok=True)

if not hasattr(aiosqlite.Connection, "is_alive"):
    def is_alive_patch(self):
        return True
    aiosqlite.Connection.is_alive = is_alive_patch

_cached_tools = []

def get_cached_tools():
    return _cached_tools

async def init_calendar_tools():
    global _cached_tools
    try:
        from backend.tools.server_mcp import MCPServer
        mcp_manager = MCPServer()
        await mcp_manager.connect()
        tools = mcp_manager.get_tools_by_namespace("google_calendar")
        _cached_tools.clear()
        _cached_tools.extend(tools)
        print(f"Herramientas de calendario cargadas: {len(_cached_tools)}")
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar herramientas de calendario: {e}")
        _cached_tools.clear()

async def router_agent():
    conn = await aiosqlite.connect(SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn)

    modelo = ChatOllama(model="gemma4:latest", temperature=0)
    all_tools = [generar_pdf_presupuesto, send_email_tool, tool_equipos, tool_presupuestos, tool_sonido] + get_cached_tools()

    router = create_react_agent(
        model=modelo,
        tools=all_tools,
        checkpointer=checkpointer,
        prompt=ROUTER_PROMPT
    )

    return router, conn
