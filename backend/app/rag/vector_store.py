"""
ChromaDB-backed vector store.

Each chunk is stored with: id (document_id:chunk_index), embedding,
document text, and metadata (document filename, category, file_type,
document_id) so deleting a document (admin document management) can cleanly
remove all of its chunks via a metadata filter.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.embeddings import get_embedding_model

logger = get_logger(__name__)


class ChromaVectorStore:
    def __init__(self, persist_dir: str | None = None, collection_name: str | None = None):
        import chromadb

        settings = get_settings()
        persist_dir = persist_dir or settings.chroma_persist_dir
        collection_name = collection_name or settings.chroma_collection_name

        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(collection_name)
        self._embedder = get_embedding_model()

    def add_chunks(self, document_id: int, filename: str, category: str, file_type: str, chunks: list[str]) -> int:
        """Embed and store all chunks for one document. Returns the number of chunks stored."""
        if not chunks:
            return 0

        ids = [f"doc{document_id}:chunk{i}" for i in range(len(chunks))]
        embeddings = self._embedder.embed(chunks)
        metadatas = [
            {"document_id": document_id, "document": filename, "category": category, "file_type": file_type, "chunk_index": i}
            for i in range(len(chunks))
        ]
        self._collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        logger.info(f"Stored {len(chunks)} chunks for document_id={document_id} ({filename})")
        return len(chunks)

    def delete_document(self, document_id: int) -> None:
        """Remove every chunk belonging to `document_id`."""
        self._collection.delete(where={"document_id": document_id})
        logger.info(f"Deleted all chunks for document_id={document_id}")

    def query(self, question: str, top_k: int) -> list[dict[str, Any]]:
        """Embed the query and return the top-k most similar chunks with metadata + relevance score."""
        if self._collection.count() == 0:
            return []

        query_embedding = self._embedder.embed_one(question)
        results = self._collection.query(
            query_embeddings=[query_embedding], n_results=min(top_k, self._collection.count())
        )

        chunks = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        for doc_text, meta, dist in zip(docs, metas, dists):
            chunks.append({"text": doc_text, "metadata": meta, "relevance": 1.0 / (1.0 + dist)})
        return chunks

    def count(self) -> int:
        return self._collection.count()


@lru_cache
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore()
