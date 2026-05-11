from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from backend.agent.prompts import BUDGET_PROMPT
from backend.agent.rag_agent import tool_equipos, tool_presupuestos, tool_sonido
from backend.tools.generate_pdf import generar_pdf_presupuesto

MODELO = "gemma4:latest"

modelo = ChatOllama(model=MODELO, temperature=0)

budget_agent = create_agent(
    model=modelo,
    tools=[tool_equipos, tool_presupuestos, tool_sonido, generar_pdf_presupuesto],
    system_prompt=BUDGET_PROMPT
)