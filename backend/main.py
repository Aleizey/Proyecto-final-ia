import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.agent.router_agent import router_agent
from backend.agent.availability_agent import get_availability_agent
from backend.agent.budget_agent import budget_agent

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
    async for paso in router_agent.astream(
        {"messages": [("user", message)]}, 
        stream_mode="values",
        config={"configurable": {"thread_id": "Alejandro"}}
    ):
        if paso["messages"]:
            ultimo_mensaje = paso["messages"][-1]
            if ultimo_mensaje.type == "ai":
                data = {
                    "content": ultimo_mensaje.content,
                    "reasoning": ultimo_mensaje.additional_kwargs.get("reasoning_content", "")
                }
                yield json.dumps(data) + "\n"

async def availability_response(message: str):
    agent = await get_availability_agent()
    async for paso in agent.astream(
        {"messages": [("user", message)]}, 
        stream_mode="values",
        config={"configurable": {"thread_id": "Availability"}}
    ):
        if paso["messages"]:
            ultimo_mensaje = paso["messages"][-1]
            if ultimo_mensaje.type == "ai":
                data = {
                    "content": ultimo_mensaje.content,
                    "reasoning": ultimo_mensaje.additional_kwargs.get("reasoning_content", "")
                }
                yield json.dumps(data) + "\n"

async def budget_response(message: str):
    async for paso in budget_agent.astream(
        {"messages": [("user", message)]}, 
        stream_mode="values",
        config={"configurable": {"thread_id": "Budget"}}
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

@app.post("/availability/stream")
async def availability_stream(request: ChatRequest):
    return StreamingResponse(availability_response(request.message), media_type="text/event-stream")

@app.post("/budget/stream")
async def budget_stream(request: ChatRequest):
    return StreamingResponse(budget_response(request.message), media_type="text/event-stream")