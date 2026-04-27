# backend/agent/rag_agent.py
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from backend.agent.prompts import RAG_PROMPT
from backend.rag.loader import configurar_parent_retriever

MODELO_LLM = "gemma4:26b"
URL_LLM = "http://192.168.117.93:11434"

retriever = configurar_parent_retriever()
tool_rag = retriever.as_tool(
    name="Busquedaequipos",
    description="Busca información sobre equipos de sonido e iluminación."
)

modelo = ChatOllama(model=MODELO_LLM, base_url=URL_LLM, temperature=0)

agente = create_agent(
    model=modelo,
    tools=[tool_rag],
    system_prompt=RAG_PROMPT
)