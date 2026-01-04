import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .database import init_db
from .middleware import OBOContextMiddleware
from .llm_agent import chat_with_agent
from .context import get_current_user_id

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# CORS (Allow everything for simplicity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Add OBO Middleware (Critical for Identity Binding)
app.add_middleware(OBOContextMiddleware)

# --- Routes ---

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat Endpoint:
    Frontend sends: {"message": "Create a note..."} with Header "Authorization: Bearer <User>"
    Middleware: Binds <User> to Context.
    Runtime: chat_with_agent() uses Context to execute OBO tools.
    """
    user_id = get_current_user_id()
    if not user_id:
        return {"error": "Authentication required"}
        
    print(f"Processing chat for User: {user_id}")
    response_text = await chat_with_agent(request.message)
    return {"response": response_text}

# Serve Frontend
# We assume the static directory is relative to this file
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))
