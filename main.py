# ─────────────────────────────────────────────
#  main.py  —  FastAPI server for portfolio chatbot
#  Run with:  uvicorn main:app --reload
# ─────────────────────────────────────────────

# ── 1. Imports ──────────────────────────────
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from rag_agent import init_rag_chatbot, get_reply
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  

# ── 2. Startup: load the chatbot once ────────
# Using lifespan so the heavy PDF + embeddings
# loading happens only ONCE when the server starts

chatbot = None   # will be set at startup

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot
    print("🚀 Starting up — loading RAG chatbot...")
    chatbot = init_rag_chatbot()   # ← heavy work done here once
    print("✅ Chatbot ready!")
    yield
    # (cleanup code could go here if needed)
    print("🛑 Shutting down")


# ── 3. Create FastAPI app ────────────────────
app = FastAPI(
    title="Asadullah Portfolio Chatbot API",
    description="RAG-powered chatbot using LangGraph + Groq + FAISS",
    version="1.0.0",
    lifespan=lifespan
)


# ── 4. CORS — allows your portfolio HTML to call this API ──
# During development: allow all origins (*)
# In production: replace * with your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # e.g. ["https://yourportfolio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Replace the broken route with this:

# ── 5. Request & Response models ─────────────
class ChatRequest(BaseModel):
    message: str           # the visitor's question
    # session_id: str = "portfolio_visitor"   # optional, ignored for now


class ChatResponse(BaseModel):
    response: str          # the AI reply
    status: str = "ok"


# ── 6. Routes ────────────────────────────────

@app.get("/")
def serve_portfolio():
    return FileResponse("static/index.html")  # ✅ Returns the actual file


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Called by your portfolio's script.js:
        fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: userText })
        })
    """
    # Guard: chatbot not ready (very rare edge case)
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not ready yet, try again in a moment")

    # Guard: empty message
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = get_reply(chatbot, request.message)
        return ChatResponse(response=reply)

    except Exception as e:
        # Log the real error on the server, return friendly message to user
        print(f"❌ Error in /chat: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")


# ── 7. How to run ─────────────────────────────
# Terminal:
#   pip install fastapi uvicorn langchain langchain-groq langchain-huggingface
#   pip install langchain-community langgraph faiss-cpu pypdf sentence-transformers python-dotenv
#
#   uvicorn main:app --reload
#
# Then update your script.js:
#   const API_ENDPOINT = 'http://localhost:8000/chat';
#
# For production deploy on Render/Railway:
#   uvicorn main:app --host 0.0.0.0 --port $PORT