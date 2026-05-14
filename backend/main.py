import json
import uuid
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware
from backend.agent.router_agent import router_agent
from backend.agent.budget_agent import budget_agent
from backend.models import ChatRequest, ConversationHistoryResponse, ConversationMeta, ConversationListResponse, CreateConversationResponse
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

def limpiar_contenido(content: str) -> str:
    content = re.sub(r'\[Document[^\]]*?\]', '', content)
    content = re.sub(r'\(\s*metadata\s*=\s*\{[^)]*\}', '', content)
    content = re.sub(r'page_content\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'producer\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'creator\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'author\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'total_pages\s*=\s*\d+', '', content)
    content = re.sub(r'page\s*=\s*\d+', '', content)
    content = re.sub(r'creationdate\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'moddate\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r'page_label\s*=\s*["\'][^"\']*["\']', '', content)
    content = re.sub(r"'source'\s*:\s*'[^']*'", '', content)
    
    lines = content.split('\n')
    cleaned_lines = []
    maraudio_count = 0
    
    for line in lines:
        stripped = line.strip()
        if '[Document' in stripped or 'metadata{' in stripped or 'page_content=' in stripped:
            continue
        if stripped == 'MARAUDIO':
            maraudio_count += 1
            if maraudio_count <= 1:
                cleaned_lines.append(line)
        else:
            if stripped:
                cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()

app = FastAPI()

os.makedirs("presupuestos", exist_ok=True)
app.mount("/presupuestos", StaticFiles(directory="presupuestos"), name="presupuestos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.agent.router_agent import SQLITE_PATH

from backend.agent.router_agent import load_calendar_tools


@app.on_event("startup")
async def startup():
    print("Precargando herramientas de calendario...")
    try:
        await load_calendar_tools()
    except Exception as e:
        print(f"Error precargando calendario: {e}")


async def get_checkpointer():
    conn = await aiosqlite.connect(SQLITE_PATH)
    return AsyncSqliteSaver(conn), conn


async def ai_response(message: str, thread_id: str):
    try:
        agent, conn = await router_agent()
        async for paso in agent.astream(
            {"messages": [("user", message)]},
            stream_mode="values",
            config={"configurable": {"thread_id": thread_id}}
        ):
            if paso["messages"]:
                ultimo_mensaje = paso["messages"][-1]
                if ultimo_mensaje.type == "ai":
                    contenido_raw = ultimo_mensaje.content
                    
                    if not contenido_raw or contenido_raw == "":
                        continue
                    
                    if not isinstance(contenido_raw, str):
                        if isinstance(contenido_raw, list):
                            texto = ""
                            for block in contenido_raw:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    texto += block.get("text", "")
                            contenido_raw = texto
                        else:
                            contenido_raw = str(contenido_raw)
                    
                    if not contenido_raw.strip():
                        continue
                    
                    content = limpiar_contenido(contenido_raw)
                    pdf_file = None

                    import re
                    match = re.search(r'presupuesto[_\s]+[^\s]+\.pdf', content)
                    if match:
                        pdf_file = match.group(0)
                    elif "PDF generado" in content:
                        archivos = os.listdir("presupuestos")
                        archivos.sort(key=lambda x: os.path.getmtime(os.path.join("presupuestos", x)), reverse=True)
                        if archivos:
                            pdf_file = archivos[0]

                    data = {
                        "content": content,
                        "reasoning": ultimo_mensaje.additional_kwargs.get("reasoning_content", ""),
                        "pdf_file": pdf_file
                    }
                    yield json.dumps(data) + "\n"
        await conn.close()
    except Exception as e:
        print(f"Error en ai_response: {e}")
        import traceback
        traceback.print_exc()
        yield json.dumps({"content": f"Error: {str(e)}", "reasoning": "", "pdf_file": None}) + "\n"

async def budget_response(message: str, thread_id: str):
    agent, conn = await budget_agent()
    async for paso in agent.astream(
        {"messages": [("user", message)]},
        stream_mode="values",
        config={"configurable": {"thread_id": thread_id}}
    ):
        if paso["messages"]:
            ultimo_mensaje = paso["messages"][-1]
            if ultimo_mensaje.type == "ai":
                data = {
                    "content": ultimo_mensaje.content,
                    "reasoning": ultimo_mensaje.additional_kwargs.get("reasoning_content", "")
                }
                yield json.dumps(data) + "\n"
    await conn.close()


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "default"
    return StreamingResponse(ai_response(request.message, thread_id), media_type="text/event-stream")


@app.post("/availability/stream")
async def availability_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "availability"
    return StreamingResponse(ai_response(request.message, thread_id), media_type="text/event-stream")


@app.post("/budget/stream")
async def budget_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "budget"
    return StreamingResponse(budget_response(request.message, thread_id), media_type="text/event-stream")


@app.get("/presupuestos")
async def list_presupuestos():
    """Lista todos los PDFs generados"""
    files = []
    for f in os.listdir("presupuestos"):
        if f.endswith(".pdf"):
            path = os.path.join("presupuestos", f)
            files.append({
                "name": f,
                "size": os.path.getsize(path),
                "url": f"/presupuestos/{f}"
            })
    return files


@app.get("/presupuestos/{filename}")
async def download_presupuesto(filename: str):
    """Descarga un PDF"""
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo archivos PDF")
    path = os.path.join("presupuestos", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@app.get("/conversations")
async def list_conversations():
    import aiosqlite
    from backend.agent.router_agent import SQLITE_PATH

    conn = await aiosqlite.connect(SQLITE_PATH)
    cursor = await conn.execute("SELECT DISTINCT thread_id FROM checkpoints")
    rows = await cursor.fetchall()
    await conn.close()

    conversations = []
    for row in rows:
        thread_id = row[0]
        conv = await get_conversation_data(thread_id)
        conversations.append(conv)

    return ConversationListResponse(conversations=conversations)


async def get_conversation_data(thread_id: str):
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from backend.agent.router_agent import SQLITE_PATH

    conn = await aiosqlite.connect(SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn)
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = await checkpointer.aget(config)

    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = await checkpointer.aget(config)

    messages = []
    title = f"Chat {thread_id}"
    preview = ""

    if checkpoint and 'channel_values' in checkpoint:
        cv = checkpoint.get('channel_values', {})
        if 'messages' in cv:
            for msg in cv['messages']:
                if hasattr(msg, 'content'):
                    messages.append({
                        "type": type(msg).__name__,
                        "content": msg.content
                    })
            if messages:
                last_msg_content = messages[-1].get("content", "")
                if isinstance(last_msg_content, list):
                    preview = str(last_msg_content[0])[:50] if last_msg_content else ""
                else:
                    preview = str(last_msg_content)[:50]
                first_user_msg = next((m for m in messages if m.get("type") == "HumanMessage"), None)
                if first_user_msg:
                    title = str(first_user_msg.get("content", ""))[:30] if isinstance(first_user_msg.get("content", ""), str) else str(first_user_msg.get("content", ""))[:30]

    await conn.close()

    return ConversationMeta(
        thread_id=thread_id,
        title=title,
        preview=preview,
        message_count=len(messages)
    )


@app.get("/conversations/{thread_id}")
async def get_conversation(thread_id: str):
    checkpointer, conn = await get_checkpointer()
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = await checkpointer.aget(config)

    messages = []
    if checkpoint and 'channel_values' in checkpoint:
        cv = checkpoint.get('channel_values', {})
        if 'messages' in cv:
            for msg in cv['messages']:
                messages.append({
                    "type": type(msg).__name__,
                    "content": msg.content if hasattr(msg, "content") else str(msg)
                })

    await conn.close()
    return ConversationHistoryResponse(thread_id=thread_id, messages=messages)


@app.post("/conversations")
async def create_conversation():
    thread_id = str(uuid.uuid4())
    return CreateConversationResponse(thread_id=thread_id)


@app.delete("/conversations/{thread_id}")
async def delete_conversation(thread_id: str):
    import aiosqlite
    from backend.agent.router_agent import SQLITE_PATH

    conn = await aiosqlite.connect(SQLITE_PATH)
    try:
        await conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        await conn.commit()
    finally:
        await conn.close()

    return {"message": "Conversation deleted", "thread_id": thread_id}
