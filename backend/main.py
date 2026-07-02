from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# In-memory storage for conversation history
# Format: {session_id: [messages]}
conversations = defaultdict(list)

class UserResponse(BaseModel):
    text: str
    session_id: str = "default"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask_llm(user_input: UserResponse):
    system_prompt = (
        "Ты — исследователь. Если ответ респондента поверхностный — задай ОДИН уточняющий вопрос. "
        "Если ответ подробный — поблагодари и заверши."
    )
    
    # Initialize history with system prompt if it's a new session
    if not conversations[user_input.session_id]:
        conversations[user_input.session_id].append({"role": "system", "content": system_prompt})
    
    # Add user message to history
    conversations[user_input.session_id].append({"role": "user", "content": user_input.text})
    
    payload = {
        "model": "openai/gpt-oss-120b", 
        "messages": conversations[user_input.session_id]
    }
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(LLM_API_URL, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            
            # Add assistant reply to history
            conversations[user_input.session_id].append({"role": "assistant", "content": reply})
            
            return {"reply": reply}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
