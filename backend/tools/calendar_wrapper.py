from langchain_core.tools import tool
import json
from datetime import datetime

_calendar_tools = {}

def set_mcp_tools(tools: list):
    global _calendar_tools
    _calendar_tools = {t.name: t for t in tools}

def _parse_mcp_response(result) -> str:
    """Convierte la respuesta MCP en texto limpio"""
    try:
        if isinstance(result, list):
            text = ""
            for block in result:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
            data = json.loads(text)
        elif isinstance(result, str):
            data = json.loads(result)
        else:
            return str(result)

        events = data.get("events", [])
        if not events:
            return "No hay eventos en el calendario."

        lines = []
        for i, ev in enumerate(events, 1):
            summary = ev.get("summary", "Sin título")
            start = ev.get("start", {})
            end = ev.get("end", {})

            if "dateTime" in start:
                try:
                    dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                    fecha = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    fecha = start["dateTime"]
            elif "date" in start:
                fecha = start["date"]
            else:
                fecha = "?"

            if "dateTime" in end:
                try:
                    dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
                    hasta = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    hasta = end["dateTime"]
            elif "date" in end:
                hasta = end["date"]
            else:
                hasta = "?"

            lines.append(f"{i}. {summary}")
            lines.append(f"   Desde: {fecha}  Hasta: {hasta}")

        return "\n".join(lines)
    except Exception as e:
        return str(result)

@tool
async def list_events(dias: int = 7) -> str:
    """Lista los próximos eventos del calendario. 
    Parámetro 'dias': cuántos días hacia adelante buscar (default 7).
    Ejemplo: list_events(dias=1) para eventos de hoy."""
    tool = _calendar_tools.get("list-events")
    if not tool:
        return "Error: Herramienta de calendario no disponible"
    try:
        from datetime import datetime, timedelta, timezone
        ahora = datetime.now(timezone.utc)
        time_min = ahora.strftime("%Y-%m-%dT%H:%M:%S")
        time_max = (ahora + timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%S")
        result = await tool.ainvoke({
            "calendarId": "primary",
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": 50
        })
        return _parse_mcp_response(result)
    except Exception as e:
        return f"Error al listar eventos: {e}"

@tool
async def search_events(consulta: str) -> str:
    """Busca eventos en el calendario por texto.
    Parámetro 'consulta': texto a buscar (ej: "reunión", "boda").
    Ejemplo: search_events(consulta="boda")"""
    tool = _calendar_tools.get("search-events")
    if not tool:
        return "Error: Herramienta de calendario no disponible"
    try:
        result = await tool.ainvoke({"calendarId": "primary", "query": consulta})
        return _parse_mcp_response(result)
    except Exception as e:
        return f"Error al buscar eventos: {e}"

@tool
async def get_event(event_id: str) -> str:
    """Obtiene los detalles de un evento específico por su ID.
    Parámetro 'event_id': el ID del evento.
    Ejemplo: get_event(event_id="abc123")"""
    tool = _calendar_tools.get("get-event")
    if not tool:
        return "Error: Herramienta de calendario no disponible"
    try:
        result = await tool.ainvoke({"calendarId": "primary", "eventId": event_id})
        return _parse_mcp_response(result)
    except Exception as e:
        return f"Error al obtener evento: {e}"

@tool
async def get_current_time() -> str:
    """Obtiene la fecha y hora actual."""
    tool = _calendar_tools.get("get-current-time")
    if not tool:
        return "Error: Herramienta de calendario no disponible"
    try:
        result = await tool.ainvoke({})
        return str(result)
    except Exception as e:
        return f"Error al obtener hora: {e}"
