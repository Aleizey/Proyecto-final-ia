from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from backend.agent.prompts import ROUTER_PROMPT
from backend.agent.rag_agent import modelo, tool_rag
from backend.tools.send_email import send_email_tool
import aiosqlite
import os

SQLITE_PATH = os.path.join("database/memoria_agente.sqlite")

os.makedirs("database", exist_ok=True)

if not hasattr(aiosqlite.Connection, "is_alive"):
    def is_alive_patch(self):
        return True
    aiosqlite.Connection.is_alive = is_alive_patch

all_tools = [
    tool_rag, 
    send_email_tool
]

async def router_agent():

    conn = await aiosqlite.connect(SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn)

    router = create_agent(
        model=modelo,
        tools=all_tools,
        checkpointer=checkpointer,
        system_prompt=ROUTER_PROMPT
    )

    return router, conn
