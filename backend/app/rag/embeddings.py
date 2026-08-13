"""Local sentence-transformers embedding model, cached as a singleton."""

from functools import lru_cache

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    def __init__(self, model_name: str | None = None):
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        logger.info(f"Loading embedding model: {self.model_name}")
        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return vectors.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()
