from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routing_agent import handle_message

app = FastAPI(title="TechStore Customer Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    agent: str
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = handle_message(request.message)
    return ChatResponse(agent=result["agent"], response=result["response"])

@app.get("/")
def root():
    return {"status": "TechStore Customer Support API is running"}