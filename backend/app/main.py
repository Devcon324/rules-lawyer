import os
import secrets
from pathlib import Path

from app.routers import auth
from app.services.RAG import RAGService
from app.utils.auth import verify_token
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

# .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)

async def lifespan(app: FastAPI):
    # Startup actions
    print(f"{'#'*80}\nStarting up the Rules Lawyer API...\n{'#'*80}")
    print(f"{'#'*80}\nInitializing RAG service...\n{'#'*80}")
    app.state.rag_service = RAGService()  # Initialize RAG service
    print(f"{'#'*80}\nBuilding embeddings...\n{'#'*80}")
    app.state.rag_service.build_embeddings(
        path_to_markdown="data/processed_documents/DRG_2E_Rulebook_docling.md")
    print(f"{'#'*80}\nBuilding query pipeline...\n{'#'*80}")
    app.state.rag_service.build_query_pipeline()
    print(f"{'#'*80}\nPre-Startup complete. Server is running...\n{'#'*80}")
    yield # Server is running
    # Shutdown actions
    print(f"{'#'*80}\nShutting down the Rules Lawyer API...\n{'#'*80}")

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

# Include routers
app.include_router(auth.router)

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

@app.get("/api/protected")
def protected_route(token_data: dict = Depends(verify_token)):
    return {"message": f"Hello {token_data['username']}"}

@app.get("/query", response_model=dict)
async def query_api(
    question: str,
    token_data: dict = Depends(verify_token)
) -> dict:
    if not question:
        return {"question": question, "answer": "No question provided."}
    rag_service: RAGService = app.state.rag_service
    answer: str = rag_service.query(question)
    return {"question": question, "answer": answer}

