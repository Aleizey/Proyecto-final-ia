from langchain.agents import create_agent
from backend.agent.prompts import BUDGET_PROMPT
from backend.tools.calc_equipos import calcular_configuracion_equipos
from .rag_agent import modelo, tool_rag
from backend.tools.server_mcp import MCPServer

mcp_manager = MCPServer()
tavily_tool = mcp_manager.get_tool_by_name("tavily")
pdf_generator_tool = mcp_manager.get_tool_by_name("pdf-generator")

if tavily_tool and pdf_generator_tool:
    tools=[calcular_configuracion_equipos, tool_rag, tavily_tool, pdf_generator_tool]

budget_agent = create_agent(
    model=modelo,
    tools=tools,
    system_prompt=BUDGET_PROMPT
)