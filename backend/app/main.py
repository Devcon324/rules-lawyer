from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from textwrap import dedent
from app.services.RAG import RAGService

# .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

async def lifespan(app: FastAPI):
    # Startup actions
    print("Starting up the Rules Lawyer API...")
    app.state.rag_service = RAGService()  # Initialize RAG service
    app.state.rag_service.build_embeddings(
        path_to_markdown="data/processed_documents/DRG_2E_Rulebook_docling.md")
    app.state.rag_service.build_query_pipeline()
    yield # Server is running
    # Shutdown actions
    print("Shutting down the Rules Lawyer API...")

app = FastAPI(
    title="Rules Lawyer API",
    description="Backend API for Rules Lawyer application",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    return {"message": "Welcome to Rules Lawyer API"}


@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "healthy"}


@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return Response(status_code=204)

@app.get("/query", response_model=dict)
async def query_api(question: str) -> dict:
    if not question:
        return {"question": question, "answer": "No question provided."}
    rag_service: RAGService = app.state.rag_service
    answer: str = rag_service.query(question)
    return {"question": question, "answer": answer}

