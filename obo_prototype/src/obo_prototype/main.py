from fastapi import FastAPI, Depends, Header
from .middleware import OBOContextMiddleware
from .mock_resource import router as mock_router
from .runtime import mock_llm_decision_making
from pydantic import BaseModel

app = FastAPI()

# 1. Add Middleware (The Binder)
app.add_middleware(OBOContextMiddleware)

# 2. Add Mock Resource (The Target)
# In real life this would be a separate microservice, but for prototype it's mounted here.
app.include_router(mock_router, prefix="/mock")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    The Agent Endpoint.
    User sends: {"message": "Show me US Sales"}
    Middleware: Captures Token.
    Runtime: Executes Tool with Token.
    """
    result = await mock_llm_decision_making(request.message)
    return {"response": result}

@app.get("/health")
def health():
    return {"status": "ok"}
