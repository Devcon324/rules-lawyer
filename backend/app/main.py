from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from textwrap import dedent
from services.RAG import RAGService

async def lifespan(app: FastAPI):
    # Startup actions
    print("Starting up the Rules Lawyer API...")
    app.state.rag_service = RAGService()  # Initialize RAG service
    app.state.rag_service.build_embeddings(
        path_to_markdown="backend/data/processed_documents/DRG_2E_Rulebook_docling.md")
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


@app.get("/", response_class=dict)
async def root():
    return {"message": "Welcome to Rules Lawyer API"}


@app.get("/health", response_class=dict)
async def health_check():
    return {"status": "healthy"}


@app.get("/favicon.ico", response_class=Response)
async def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return Response(status_code=204)

@app.get("/query", response_class=dict)
async def query_api(question: str) -> dict:
    rag_service: RAGService = app.state.rag_service
    answer: str = rag_service.query(question)
    return {"question": question, "answer": answer}


if __name__ == "__main__":
  uvicorn.run(
    app="main:app",
    host="127.0.0.1",
    port=8000,
    reload=True
  )