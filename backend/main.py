from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from backend.agent.rag_agent import agente

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

async def ai_response(message: str):
    async for paso in agente.astream(
        {"messages": [("user", message)]}, 
        stream_mode="values"
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
    return StreamingResponse(ai_response(request.message), media_type="text/event-stream")