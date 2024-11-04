from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize FastAPI
app = FastAPI()

# Allow CORS
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the chatbot template and model
template = """
You are an assistant. Answer the user's question directly without any prefixes or extra commentary.

User: {question}
Assistant:
"""

model = OllamaLLM(model="llama3.2:1b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Track conversation history
class Conversation:
    def __init__(self):
        self.context = ""  # Start with an empty context for direct responses

    def update_context(self, user_input, bot_response):
        # Store the user input and bot response without prefixes
        self.context += f"\nUser: {user_input}\nBot: {bot_response}\n"

    def reset_context(self):
        self.context = ""  # Reset to empty context

# Create an instance to store the conversation
conversation = Conversation()

# Define the request body model
class UserInput(BaseModel):
    user_input: str
    reset_context: bool = False  # Default to False

@app.post("/chat")
async def chat(input: UserInput):
    # Reset context if requested
    if input.reset_context:
        conversation.reset_context()

    # Prepare the context without prefixes for processing
    context_start = conversation.context.strip()

    # Process the user input through the model
    result = chain.invoke({
        "context_start": context_start,
        "question": input.user_input.strip()
    })

    # Update the context with the current user input and the bot response
    conversation.update_context(input.user_input, result)

    # Return the bot's response directly, ensuring no prefixes
    return {"bot_response": result.strip()}

@app.post("/reset")
async def reset_conversation():
    conversation.reset_context()
    # Return a new introduction message along with the reset notification
    introduction_message = "Hello! How can I assist you today?"
    return {
        "message": "Conversation context has been reset.",
        "introduction": introduction_message
    }

