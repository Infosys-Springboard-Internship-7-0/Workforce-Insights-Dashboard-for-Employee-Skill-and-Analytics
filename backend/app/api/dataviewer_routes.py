"""
Data Viewer routes.

Public per the platform spec (Home / Chatbot / PowerBI / Data Viewer are all
general-audience pages; only login + admin management are admin-gated).
Lists uploaded CSV datasets and returns their content as paginated JSON
table data (columns + rows), read fresh from the stored CSV via pandas so
the viewer always reflects the actual file on disk. Uploading/deleting
datasets remains admin-only via /api/documents.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/api/data-viewer", tags=["data-viewer"])


@router.get("/datasets", response_model=list[DocumentOut])
async def list_datasets(db: Session = Depends(get_db)) -> list[DocumentOut]:
    """List every uploaded CSV dataset (public)."""
    docs = db.execute(
        select(Document).where(Document.file_type == "csv").order_by(Document.uploaded_at.desc())
    ).scalars().all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/datasets/{document_id}")
async def get_dataset_table(
    document_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> dict:
    """Return a page of table rows for one CSV dataset, plus total row count for pagination (public)."""
    import pandas as pd

    doc = db.get(Document, document_id)
    if doc is None or doc.file_type != "csv":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CSV dataset not found.")

    try:
        df = pd.read_csv(doc.stored_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read dataset: {exc}") from exc

    total_rows = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end].fillna("")

    return {
        "filename": doc.filename,
        "columns": list(df.columns.astype(str)),
        "rows": page_df.to_dict(orient="records"),
        "total_rows": total_rows,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total_rows + page_size - 1) // page_size),
    }
