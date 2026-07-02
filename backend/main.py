from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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

class UserResponse(BaseModel):
    text: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask_llm(user_input: UserResponse):
    system_prompt = (
        "Ты — исследователь. Если ответ респондента поверхностный — задай ОДИН уточняющий вопрос. "
        "Если ответ подробный — поблагодари и заверши."
    )
    
    payload = {
        "model": "openai/gpt-oss-120b", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input.text}
        ]
    }
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending request to {LLM_API_URL} with key {LLM_API_KEY[:10]}...")
            response = await client.post(LLM_API_URL, json=payload, headers=headers, timeout=30.0)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            return {"reply": data["choices"][0]["message"]["content"]}
        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
