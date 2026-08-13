"""
Admin document ingestion: Extract Text -> Chunk -> Embedding -> Store in ChromaDB.

This is the single function the documents API route calls after saving an
uploaded file to disk, so upload handling and ingestion logic stay
separated and independently testable.
"""

from pathlib import Path

from app.rag.chunker import chunk_text
from app.rag.extractors import ExtractionError, extract_text
from app.rag.vector_store import get_vector_store


def ingest_document(document_id: int, path: Path, filename: str, category: str, file_type: str) -> int:
    """
    Run the full ingestion pipeline for one already-saved file and return
    the number of chunks stored. Raises ExtractionError on unreadable files.
    """
    text = extract_text(path)
    chunks = chunk_text(text)
    if not chunks:
        raise ExtractionError(f"'{filename}' produced no usable chunks after cleaning.")

    store = get_vector_store()
    return store.add_chunks(document_id=document_id, filename=filename, category=category, file_type=file_type, chunks=chunks)
