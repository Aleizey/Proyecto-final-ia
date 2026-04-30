from langchain.agents import create_agent
from backend.agent.prompts import AVAILABILITY_PROMPT
from backend.tools.check_agenda import consultar_disponibilidad
from .rag_agent import modelo
# from langchain_google_community import GoogleCalendarToolkit


# toolkit = GoogleCalendarToolkit()
# tools = toolkit.get_tools()
tools.append(consultar_disponibilidad)

availability_agent = create_agent(
    model=modelo,
    tools=tools,
    system_prompt=AVAILABILITY_PROMPT
)