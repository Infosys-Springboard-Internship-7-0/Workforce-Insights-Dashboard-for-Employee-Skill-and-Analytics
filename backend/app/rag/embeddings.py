from functools import lru_cache
from huggingface_hub import InferenceClient
from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_embedding_client():
    return InferenceClient(api_key=settings.hf_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_embedding_client()
    vectors = client.feature_extraction(text=texts, model=settings.embedding_model)
    return vectors


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
