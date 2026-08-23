from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.rag.embeddings import embed_query


def search_chunks(
    db: Session,
    question: str,
    top_k: int = 5,
    document_filename: str | None = None,
):
    vector = embed_query(question)

    distance = DocumentChunk.embedding.cosine_distance(vector)

    stmt = (
        select(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    if document_filename:
        stmt = stmt.where(Document.filename == document_filename)

    return db.execute(stmt).scalars().all()
