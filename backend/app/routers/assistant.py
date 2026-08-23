from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.document import Document
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.get("/documents")
def indexed_documents(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List indexed uploaded files available to the assistant."""
    documents = db.scalars(
        select(Document)
        .where(Document.status == "indexed")
        .order_by(Document.created_at.desc())
    ).all()
    return [
        {
            "filename": document.filename,
            "chunk_count": document.chunk_count,
            "file_type": document.file_type,
        }
        for document in documents
    ]


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    answer, session_id, sources = answer_question(
        db,
        user.id,
        payload.question,
        payload.dataset_name,
        payload.document_filename,
    )
    return {
        "answer": answer,
        "session_id": session_id,
        "sources": sources,
    }


@router.get("/suggestions")
def suggestions():
    return {
        "questions": [
            "What is the project architecture?",
            "What technologies are being used?",
            "Summarize the project documentation.",
            "What are the major findings from the dataset?",
            "What recommendations can be made?",
            "Explain the RAG pipeline.",
        ]
    }
