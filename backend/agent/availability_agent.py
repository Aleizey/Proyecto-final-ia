from .rag_agent import modelo
from langchain.agents import create_agent
from backend.agent.prompts import AVAILABILITY_PROMPT
from backend.tools.server_mcp import MCPServer

mcp_manager = MCPServer()

async def availability_agent():

    await mcp_manager.connect() 
    calendar_tools = mcp_manager.get_tools_by_namespace("google_calendar")

    agent = create_agent(
        model=modelo,
        tools=calendar_tools,
        system_prompt=AVAILABILITY_PROMPT
    )
    return agent