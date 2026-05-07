from langchain.agents import create_agent
from backend.agent.prompts import BUDGET_PROMPT
from .rag_agent import modelo, tool_rag
from backend.tools.generate_pdf import generar_pdf_presupuesto
from backend.tools.server_mcp import MCPServer

mcp_manager = MCPServer()
tools = [tool_rag, generar_pdf_presupuesto]

tavily_tool = mcp_manager.get_tool_by_name("tavily")
if tavily_tool:
    tools.append(tavily_tool)

budget_agent = create_agent(
    model=modelo,
    tools=tools,
    system_prompt=BUDGET_PROMPT
)