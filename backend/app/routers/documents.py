from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_admin
from app.models.document import Document
from app.models.user import User
from app.services.rag_service import ingest_document
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/admin/documents", tags=["documents"])


class DocumentMetadataUpdate(BaseModel):
    description: str = None
    filename: str = None


@router.get("")
def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if status:
        docs = DocumentService.get_documents_by_status(db, status, skip, limit)
    else:
        docs = DocumentService.get_all_documents(db, skip, limit)
    
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "description": d.description,
            "file_type": d.file_type,
            "status": d.status,
            "processing_status": d.processing_status,
            "chunk_count": d.chunk_count,
            "uploaded_by": d.uploaded_by,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
        }
        for d in docs
    ]


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "description": document.description,
        "file_type": document.file_type,
        "status": document.status,
        "processing_status": document.processing_status,
        "chunk_count": document.chunk_count,
        "uploaded_by": document.uploaded_by,
        "file_path": document.file_path,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    allowed = {".pdf", ".docx", ".txt", ".csv"}
    suffix = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Supported formats: PDF, DOCX, TXT, CSV")

    content = await file.read()

    document = DocumentService.create_document(
        db,
        filename=file.filename,
        file_type=suffix[1:],
        uploaded_by=user.id,
        description=description,
    )

    try:
        ingest_document(db, content, file.filename, document)
    except Exception as exc:
        DocumentService.update_document_status(db, document.id, "failed", str(exc))
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "message": "Document indexed",
        "id": document.id,
        "filename": document.filename,
        "chunks": document.chunk_count,
    }


@router.put("/{document_id}")
def update_document(
    document_id: str,
    payload: DocumentMetadataUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    document = DocumentService.update_document_metadata(
        db,
        document_id,
        description=payload.description,
        filename=payload.filename,
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "message": "Document updated",
        "id": document.id,
        "filename": document.filename,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document and vector chunks deleted", "id": document_id}
