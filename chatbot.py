from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

# A simple model to receive messages
class Message(BaseModel):
    user: str
    text: str

# Sample responses for the chatbot
responses = [
    "Hello! How can I help you today?",
    "I'm just a bot, but I can chat with you!",
    "What would you like to talk about?",
    "I'm here to listen!",
]

@app.post("/chatbot/")
async def chat(message: Message):
    # Generate a random response
    bot_response = random.choice(responses)
    return {"bot_response": bot_response}
