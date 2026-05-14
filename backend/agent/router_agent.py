from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from backend.agent.prompts import ROUTER_PROMPT
from backend.agent.rag_agent import tool_equipos, tool_presupuestos, tool_sonido
from backend.tools.send_email import enviar_email_presupuesto
from backend.tools.generate_pdf import generar_pdf_presupuesto
import aiosqlite
import os

SQLITE_PATH = os.path.join("database/memoria_agente.sqlite")

os.makedirs("database", exist_ok=True)

if not hasattr(aiosqlite.Connection, "is_alive"):
    def is_alive_patch(self):
        return True
    aiosqlite.Connection.is_alive = is_alive_patch

_cached_calendar_tools = []
_calendar_loading = False

async def load_calendar_tools():
    global _cached_calendar_tools, _calendar_loading
    if _cached_calendar_tools:
        return _cached_calendar_tools
    if _calendar_loading:
        return []
    _calendar_loading = True
    try:
        from backend.tools.server_mcp import MCPServer
        from backend.tools.calendar_wrapper import set_mcp_tools, list_events, search_events, get_event, get_current_time
        mcp_manager = MCPServer()
        await mcp_manager.connect()
        mcp_tools = mcp_manager.get_tools_by_namespace("google_calendar")
        set_mcp_tools(mcp_tools)
        _cached_calendar_tools = [list_events, search_events, get_event, get_current_time]
        print(f"Herramientas de calendario cargadas: {len(_cached_calendar_tools)}")
        tool_names = [t.name for t in _cached_calendar_tools]
        print(f"  - {tool_names}")
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar herramientas de calendario: {e}")
        _cached_calendar_tools = []
    return _cached_calendar_tools

async def router_agent():
    conn = await aiosqlite.connect(SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn)

    modelo = ChatOllama(model="qwen2.5:3b", temperature=0)
    
    calendar_tools = await load_calendar_tools()
    
    base_tools = [generar_pdf_presupuesto, enviar_email_presupuesto, tool_equipos, tool_presupuestos, tool_sonido]
    all_tools = base_tools + calendar_tools
    print(f"[DEBUG] Herramientas: {[t.name for t in all_tools]}")

    router = create_react_agent(
        model=modelo,
        tools=all_tools,
        checkpointer=checkpointer,
        prompt=ROUTER_PROMPT
    )

    return router, conn
