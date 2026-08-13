"""Document metadata schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    category: str
    chunk_count: int
    uploaded_by: str
    uploaded_at: datetime
    model_config = {"from_attributes": True}


class PublicDocumentSummary(BaseModel):
    """Minimal, public-safe document listing (no uploader email) for the landing page."""

    id: int
    filename: str
    file_type: str
    category: str
    model_config = {"from_attributes": True}


class DocumentUpdateRequest(BaseModel):
    category: str | None = Field(default=None, max_length=100)


class DocumentUploadResponse(BaseModel):
    document: DocumentOut
    chunks_created: int
