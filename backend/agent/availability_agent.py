from langchain.agents import create_agent
from backend.agent.prompts import AVAILABILITY_PROMPT
from backend.tools.check_agenda import consultar_disponibilidad
from .rag_agent import modelo

availability_agent = create_agent(
    model=modelo,
    tools=[consultar_disponibilidad],
    system_prompt=AVAILABILITY_PROMPT
)