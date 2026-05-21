# ─────────────────────────────────────────────
#  rag_agent.py  —  RAG logic for portfolio chatbot
#  Uses: LangGraph + Groq LLM + FAISS + HuggingFace embeddings
# ─────────────────────────────────────────────

# ── 1. Imports ──────────────────────────────
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict
from dotenv import load_dotenv
import os
import logging

logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

load_dotenv()  # loads GROQ_API_KEY from your .env file


# ── 2. LLM setup ────────────────────────────
# Make sure your .env has: GROQ_API_KEY=your_key_here
llm = ChatGroq(model="openai/gpt-oss-120b")   # free & fast Groq model


# ── 3. Load & chunk the PDF ─────────────────
PDF_PATH = "./resume.pdf"   # put your resume PDF next to this file

def load_pdf(path: str):
    print(f"📄 Loading PDF: {path}")
    loader = PyPDFLoader(path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"✅ Loaded {len(docs)} pages → {len(chunks)} chunks from PDF")
    return chunks


# ── 4. Build FAISS vector store ─────────────
def build_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    print("✅ Vector store ready")
    return retriever


# ── 5. RAG tool (used by LangGraph agent) ───
# We build the tool after we have the retriever
def make_rag_tool(retriever):

    @tool
    def rag_tool(query: str) -> dict:
        """Retrieve relevant information about Asadullah from his resume PDF."""
        results = retriever.invoke(query)
        context = [doc.page_content for doc in results]
        return {"query": query, "context": context}

    return rag_tool


# ── 6. LangGraph state ───────────────────────
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ── 7. Build the LangGraph chatbot ──────────
def build_chatbot(rag_tool):
    tools = [rag_tool]
    llm_with_tools = llm.bind_tools(tools)

    # System prompt — tells the LLM who it is
    SYSTEM_PROMPT = """You are a helpful AI assistant of Asadullah Shehbaz.
Answer visitor questions about Asadullah's skills, projects, experience, certifications, and services.
Always use the rag_tool to fetch accurate information from his resume.
Be friendly, concise, and professional. If you don't know something, say so honestly.
- Never output tables unless explicitly requested."""

    def chat_node(state: ChatState):
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    # Build graph
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()
    print("✅ LangGraph chatbot compiled")
    return chatbot


# ── 8. Main function to get a reply ─────────
def get_reply(chatbot, user_message: str) -> str:
    """Send a message and get the AI reply as a string."""
    response = chatbot.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return response["messages"][-1].content


# ── 9. One-time initialization ───────────────
# Called once at app startup — not on every request
def init_rag_chatbot():

    chunks = load_pdf(PDF_PATH)
    print(f"Loaded {len(chunks)} chunks from PDF")
    retriever = build_vector_store(chunks)
    print(f" Vector store ready")
    rag_tool = make_rag_tool(retriever)
    print(f" RAG tool ready")
    chatbot = build_chatbot(rag_tool)
    print(f"Chatbot ready")
    return chatbot

if __name__ == "__main__":
    
    chunks = load_pdf(PDF_PATH)
    print(f"Loaded {len(chunks)} chunks from PDF")
    retriever = build_vector_store(chunks)
    print(f" Vector store ready")
    rag_tool = make_rag_tool(retriever)
    print(f" RAG tool ready")
    chatbot = build_chatbot(rag_tool)
    print(f"Chatbot ready")

    while True:
        user_message = input("You: ")
        reply = get_reply(chatbot, user_message)
        print("AI:", reply)