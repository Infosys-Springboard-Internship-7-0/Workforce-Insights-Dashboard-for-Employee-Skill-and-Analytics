"""
Document metadata model.

The actual extracted text/embeddings live in ChromaDB (see app/rag/); this
table tracks admin-facing metadata (filename, type, status, who uploaded,
when) so the admin document-management page can list/update/delete
documents without touching Chroma directly for simple metadata edits.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf / docx / txt / csv
    category: Mapped[str] = mapped_column(String(100), default="General")  # e.g. "Policy", "Privacy", "Report"
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)  # admin email
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
