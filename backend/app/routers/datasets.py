from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.dataset import Dataset, DatasetRow
from app.models.user import User
from app.rag.embeddings import embed_query, embed_texts
from app.schemas.dataset import DatasetCreate, DatasetUpdate, RowCreate, RowUpdate, SemanticSearchRequest

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


def _row_to_text(data: dict[str, Any]) -> str:
    return " | ".join(f"{key}: {value}" for key, value in data.items() if value is not None)


def _serialize_dataset(dataset: Dataset) -> dict:
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "columns": dataset.columns or [],
        "row_count": dataset.row_count,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
        "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
    }


def _serialize_row(row: DatasetRow) -> dict:
    return {
        "id": row.id,
        "dataset_id": row.dataset_id,
        "row_index": row.row_index,
        "data": row.data,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get("")
def list_datasets(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    datasets = db.scalars(select(Dataset).order_by(Dataset.updated_at.desc())).all()
    return [_serialize_dataset(item) for item in datasets]


@router.post("")
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    dataset = Dataset(name=payload.name.strip(), description=payload.description.strip())
    db.add(dataset)
    try:
        db.commit()
        db.refresh(dataset)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A dataset with this name already exists")
    return _serialize_dataset(dataset)


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return _serialize_dataset(dataset)


@router.put("/{dataset_id}")
def update_dataset(dataset_id: str, payload: DatasetUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if payload.name is not None:
        dataset.name = payload.name.strip()
    if payload.description is not None:
        dataset.description = payload.description.strip()
    try:
        db.commit()
        db.refresh(dataset)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A dataset with this name already exists")
    return _serialize_dataset(dataset)


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted", "id": dataset_id}


@router.post("/{dataset_id}/upload")
def upload_csv(
    dataset_id: str,
    file: UploadFile = File(...),
    replace_existing: bool = Form(False),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = file.file.read()

        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

        df = None
        last_error = None

        for encoding in encodings:
            try:
                df = pd.read_csv(BytesIO(contents), encoding=encoding)
                break
            except UnicodeDecodeError as exc:
                last_error = exc

        if df is None:
            raise ValueError(
                f"Unsupported CSV encoding. Last error: {last_error}"
            )

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}")

    # Normalize NaN/NumPy values into JSON-safe Python values.
    df = df.astype(object).where(pd.notna(df), None)
    records = df.to_dict(orient="records")
    columns = [str(col) for col in df.columns]

    if replace_existing:
        db.query(DatasetRow).filter(DatasetRow.dataset_id == dataset_id).delete(synchronize_session=False)
    elif dataset.row_count:
        raise HTTPException(status_code=409, detail="Dataset already contains rows. Use replace_existing=true to replace them.")

    texts = [_row_to_text(record) for record in records]
    vectors = embed_texts(texts) if texts else []
    rows = []
    for index, (record, text, vector) in enumerate(zip(records, texts, vectors)):
        clean_record = {str(k): v for k, v in record.items()}
        rows.append(DatasetRow(dataset_id=dataset_id, row_index=index, data=clean_record, search_text=text, embedding=vector))

    if rows:
        db.add_all(rows)
    dataset.columns = columns
    dataset.row_count = len(rows)
    db.commit()
    return {"message": "CSV imported", "dataset": _serialize_dataset(dataset), "imported_rows": len(rows)}


@router.get("/{dataset_id}/rows")
def list_rows(
    dataset_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    stmt = select(DatasetRow).where(DatasetRow.dataset_id == dataset_id)
    count_stmt = select(func.count()).select_from(DatasetRow).where(DatasetRow.dataset_id == dataset_id)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        condition = DatasetRow.search_text.ilike(pattern)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.order_by(DatasetRow.row_index).offset((page - 1) * limit).limit(limit)).all()
    return {
        "dataset": _serialize_dataset(dataset),
        "page": page,
        "limit": limit,
        "total": int(total),
        "pages": max(1, (int(total) + limit - 1) // limit),
        "rows": [_serialize_row(row) for row in rows],
    }


@router.post("/{dataset_id}/rows")
def create_row(dataset_id: str, payload: RowCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    max_index = db.scalar(select(func.max(DatasetRow.row_index)).where(DatasetRow.dataset_id == dataset_id))
    row_index = 0 if max_index is None else int(max_index) + 1
    text = _row_to_text(payload.data)
    row = DatasetRow(dataset_id=dataset_id, row_index=row_index, data=payload.data, search_text=text, embedding=embed_query(text) if text else None)
    db.add(row)
    dataset.columns = list(dict.fromkeys([*(dataset.columns or []), *payload.data.keys()]))
    dataset.row_count += 1
    db.commit()
    db.refresh(row)
    return _serialize_row(row)


@router.put("/{dataset_id}/rows/{row_id}")
def update_row(dataset_id: str, row_id: str, payload: RowUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    row = db.scalar(select(DatasetRow).where(DatasetRow.id == row_id, DatasetRow.dataset_id == dataset_id))
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    text = _row_to_text(payload.data)
    row.data = payload.data
    row.search_text = text
    row.embedding = embed_query(text) if text else None
    dataset = db.get(Dataset, dataset_id)
    dataset.columns = list(dict.fromkeys([*(dataset.columns or []), *payload.data.keys()]))
    db.commit()
    db.refresh(row)
    return _serialize_row(row)


@router.delete("/{dataset_id}/rows/{row_id}")
def delete_row(dataset_id: str, row_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    row = db.scalar(select(DatasetRow).where(DatasetRow.id == row_id, DatasetRow.dataset_id == dataset_id))
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    db.delete(row)
    dataset = db.get(Dataset, dataset_id)
    dataset.row_count = max(0, dataset.row_count - 1)
    db.commit()
    return {"message": "Row deleted", "id": row_id}


@router.post("/{dataset_id}/search")
def semantic_search(dataset_id: str, payload: SemanticSearchRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    query_vector = embed_query(payload.query)
    distance = DatasetRow.embedding.cosine_distance(query_vector)
    stmt = (
        select(DatasetRow, (1 - distance).label("similarity"))
        .where(DatasetRow.dataset_id == dataset_id, DatasetRow.embedding.is_not(None))
        .order_by(distance)
        .limit(payload.limit)
    )
    results = db.execute(stmt).all()
    return {
        "query": payload.query,
        "results": [
            {**_serialize_row(row), "similarity": round(float(similarity), 6)}
            for row, similarity in results
        ],
    }
