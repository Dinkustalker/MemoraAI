from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")

print("KEY START:", key[:10] if key else "NO KEY")
print("KEY LENGTH:", len(key) if key else 0)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=key)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are MemoraAI, an elderly healthcare AI assistant.

Rules:
- Use simple language.
- Do not give final diagnosis.
- Do not prescribe medicines.
- Ask the user to consult a doctor for serious symptoms.
- For emergency symptoms, advise emergency medical help.
"""
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            temperature=0.3
        )

        return {
            "answer": response.choices[0].message.content
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "answer": "Backend error: " + str(e)
        }