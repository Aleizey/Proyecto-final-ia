import json
import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.agent.router_agent import router_agent
from backend.agent.availability_agent import availability_agent
from backend.agent.budget_agent import budget_agent
from backend.models import ChatRequest, ConversationHistoryResponse, ConversationMeta, ConversationListResponse, CreateConversationResponse
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.agent.router_agent import SQLITE_PATH


async def get_checkpointer():
    conn = await aiosqlite.connect(SQLITE_PATH)
    return AsyncSqliteSaver(conn), conn


async def ai_response(message: str, thread_id: str):
    agent, conn = await router_agent()
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

async def availability_response(message: str, thread_id: str):
    agent = await availability_agent()
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

async def budget_response(message: str, thread_id: str):
    agent = budget_agent
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


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "default"
    return StreamingResponse(ai_response(request.message, thread_id), media_type="text/event-stream")


@app.post("/availability/stream")
async def availability_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "availability"
    return StreamingResponse(availability_response(request.message, thread_id), media_type="text/event-stream")


@app.post("/budget/stream")
async def budget_stream(request: ChatRequest):
    thread_id = request.thread_id if request.thread_id != "default" else "budget"
    return StreamingResponse(budget_response(request.message, thread_id), media_type="text/event-stream")


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
                preview = messages[-1].get("content", "")[:50]
                first_user_msg = next((m for m in messages if m.get("type") == "HumanMessage"), None)
                if first_user_msg:
                    title = first_user_msg.get("content", title)[:30]
    
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