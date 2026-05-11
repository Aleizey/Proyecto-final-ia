# backend/agent/rag_agent.py
from backend.rag.loader import get_retriever

tool_equipos = get_retriever("equipos").as_tool(
    name="BusquedaEquipos",
    description="Busca información sobre equipos de sonido, iluminacion e infraestructura tecnica. USA ESTA HERRAMIENTA cuando el usuario pregunte sobre equipos especificos, caracteristicas tecnicas, marcas o modelos."
)

tool_presupuestos = get_retriever("presupuestos").as_tool(
    name="BusquedaPresupuestos",
    description="Busca informacion sobre tarifas, precios y plantillas de presupuestos. USA ESTA HERRAMIENTA cuando el usuario pregunte sobre precios, tarifas o quiera hacer un presupuesto."
)

tool_sonido = get_retriever("sonido").as_tool(
    name="BusquedaSonido",
    description="Busca informacion sobre configuracion de PA, teoria de sonido, acustica y mezcladoras. USA ESTA HERRAMIENTA cuando el usuario pregunte sobre configuracion de audio, consejos de sonido o teoria acustica."
)