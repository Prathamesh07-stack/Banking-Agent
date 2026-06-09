import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from Agents.router_agent import RouterAgent

app = FastAPI(title="BankBot API", version="1.0.0")

# Allow the Vite dev server (port 5173) to talk to FastAPI (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared RouterAgent instance (holds chat history in memory)
gemini_key = os.getenv("GOOGLE_API_KEY", "")
groq_key   = os.getenv("GROQ_API_KEY", "")
router = RouterAgent(gemini_api_key=gemini_key, groq_api_key=groq_key)

#request  models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    agent_label: str

# helpers
AGENT_LABELS = {
    "banking_agent": "Knowledge",
    "search_agent":  "Live Search",
    "refusal":       "Out of scope",
    "none":          "",
}

# endpoints

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    response, agent_used = router.chat(req.message)
    return ChatResponse(
        response=response,
        agent_used=agent_used,
        agent_label=AGENT_LABELS.get(agent_used, agent_used),
    )

@app.post("/reset")
def reset():
    router.reset()
    return {"status": "reset", "message": "Conversation history cleared."}