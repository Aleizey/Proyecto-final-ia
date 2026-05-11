from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from backend.agent.prompts import AVAILABILITY_PROMPT
from backend.tools.server_mcp import MCPServer

MODELO = "gemma4:latest"

mcp_manager = MCPServer()

async def availability_agent():
    modelo = ChatOllama(model=MODELO, temperature=0)
    await mcp_manager.connect()
    calendar_tools = mcp_manager.get_tools_by_namespace("google_calendar")

    agent = create_agent(
        model=modelo,
        tools=calendar_tools,
        system_prompt=AVAILABILITY_PROMPT
    )
    return agent