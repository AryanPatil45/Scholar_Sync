from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from src.services.document_service import DocumentService
from src.repositories.vector_repo import VectorRepo
from src.services.rag_service import RAGService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Scholar-Sync API",
    description="Multilingual Local RAG Backend",
    version="1.0.0"
)

# --- CORS BLOCK (Allows React to talk to FastAPI) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our business logic and AI services
doc_service = DocumentService()
vector_repo = VectorRepo()
rag_service = RAGService(vector_repo)

# --- Data Models ---
class QuestionRequest(BaseModel):
    question: str
    language: str = "English"
    mode: str = "Academic"

# --- Endpoints ---
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        file_bytes = await file.read()
        chunks = doc_service.process_pdf(file_bytes, file.filename)
        if chunks:
            vector_repo.add_chunks(chunks)
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/upload_ppt")
async def upload_ppt(file: UploadFile = File(...)) -> dict:
    if not (file.filename.endswith('.pptx') or file.filename.endswith('.ppt')):
        raise HTTPException(status_code=400, detail="Only PPTX/PPT files are allowed.")
    
    try:
        file_bytes = await file.read()
        chunks = doc_service.process_ppt(file_bytes, file.filename)
        if chunks:
            vector_repo.add_chunks(chunks)
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PPT: {str(e)}")

@app.post("/ask")
async def ask_question(req: QuestionRequest) -> dict:
    try:
        result = rag_service.ask_question(req.question, req.language, req.mode)
        return {
            "status": "success",
            "answer": result["answer"],
            "sources_used": len(result["sources"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.delete("/clear")
async def clear_memory():
    try:
        vector_repo.clear_memory()
        return {"status": "success", "message": "Memory wiped clean!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")

@app.post("/quiz")
async def generate_quiz(req: QuestionRequest) -> dict:
    try:
        result = rag_service.generate_quiz(req.language, req.mode)
        return {
            "status": "success",
            "quiz": result["quiz"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")