"""
Document management routes (admin-only).

Upload -> Extract Text -> Chunk -> Embedding -> Store in ChromaDB, per the
specified pipeline. Deleting a document removes both its DB metadata row
and its chunks from ChromaDB, so the two stores never drift out of sync.
"""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.document import Document
from app.rag.extractors import ExtractionError
from app.rag.ingest import ingest_document
from app.rag.vector_store import get_vector_store
from app.schemas.document import DocumentOut, DocumentUpdateRequest, DocumentUploadResponse, PublicDocumentSummary

router = APIRouter(prefix="/api/documents", tags=["documents"])
logger = get_logger(__name__)

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}


@router.get("/public", response_model=list[PublicDocumentSummary])
async def list_documents_public(db: Session = Depends(get_db)) -> list[PublicDocumentSummary]:
    """Public, minimal document listing (filename/type/category only) for the landing page."""
    docs = db.execute(select(Document).order_by(Document.uploaded_at.desc())).scalars().all()
    return [PublicDocumentSummary.model_validate(d) for d in docs]


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    file_type: str | None = None, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> list[DocumentOut]:
    query = select(Document).order_by(Document.uploaded_at.desc())
    if file_type:
        query = query.where(Document.file_type == file_type.lower())
    docs = db.execute(query).scalars().all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    category: str = "General",
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    settings = get_settings()
    suffix = Path(file.filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{suffix}'. Allowed: PDF, DOCX, TXT, CSV.")

    dest_dir = Path(settings.documents_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    try:
        with dest_path.open("wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not save file: {exc}") from exc

    doc = Document(
        filename=file.filename,
        stored_path=str(dest_path),
        file_type=suffix.lstrip("."),
        category=category,
        uploaded_by=current_admin.email,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        chunk_count = ingest_document(
            document_id=doc.id, path=dest_path, filename=file.filename, category=category, file_type=doc.file_type
        )
    except ExtractionError as exc:
        db.delete(doc)
        db.commit()
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    doc.chunk_count = chunk_count
    db.commit()
    db.refresh(doc)

    logger.info(f"Ingested '{file.filename}' ({chunk_count} chunks) uploaded by {current_admin.email}")
    return DocumentUploadResponse(document=DocumentOut.model_validate(doc), chunks_created=chunk_count)


@router.put("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: int,
    request: DocumentUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DocumentOut:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if request.category is not None:
        doc.category = request.category
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> None:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    get_vector_store().delete_document(document_id)
    Path(doc.stored_path).unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
