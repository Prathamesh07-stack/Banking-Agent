import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph.bankbot_graph import BankBotGraph

load_dotenv()

app = FastAPI(
    title="BankBot API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_key = os.getenv("GOOGLE_API_KEY", "")
groq_key = os.getenv("GROQ_API_KEY", "")

bot = BankBotGraph(
    gemini_api_key=gemini_key,
    groq_api_key=groq_key
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    agent_label: str

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):

    result = bot.graph.invoke(
        {
            "query": req.message
        },
        config={
            "configurable": {
                "thread_id": req.session_id
            }
        }
    )

    return ChatResponse(
        response=result["response"],
        agent_used=result["agent_used"],
        agent_label=result["agent_label"]
    )


@app.post("/reset")
def reset():
    return {
        "status": "info",
        "message": (
            "LangGraph MemorySaver does not support "
            "manual reset. Start a new session_id."
        )
    }