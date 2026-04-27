from langchain.agents import create_agent
from backend.agent.prompts import ROUTER_PROMPT
from backend.agent.rag_agent import modelo, tool_rag
#from backend.tools.check_agenda import consultar_disponibilidad
#from backend.tools.calc_equipos import calcular_configuracion_equipos
from backend.tools.send_email import send_email_tool


all_tools = [
    
    tool_rag, 
    #consultar_disponibilidad, 
    #calcular_configuracion_equipos,
    send_email_tool
]

router_agent = create_agent(
    model=modelo,
    tools=all_tools,
    system_prompt=ROUTER_PROMPT
)