"""
End-to-end integration test for the chat pipeline through the real API:
upload -> ingest -> chat query -> Groq call -> cited answer.

Both the embedding model and the Groq LLM call are mocked (no network),
but every other layer (FastAPI route, ChromaDB storage/retrieval, prompt
construction, response assembly) runs for real.
"""

import hashlib
import io
from unittest.mock import patch

import pytest


class _FakeEmbeddingModel:
    def embed(self, texts):
        return [[b / 255.0 for b in hashlib.md5(t.encode()).digest()[:8]] for t in texts]

    def embed_one(self, text):
        return self.embed([text])[0]


@pytest.fixture(autouse=True)
def _patch_embeddings(monkeypatch, request):
    import app.rag.vector_store as vs_mod
    from app.core.config import get_settings

    # Give this test its own ChromaDB collection so leftover chunks from
    # other tests (sharing the session-wide persist directory) can never
    # leak in. The fake embedder's similarity scores are semantically
    # meaningless noise, so a leftover chunk from another test could
    # otherwise spuriously look "relevant" to an unrelated query.
    unique_collection = f"test_{abs(hash(request.node.nodeid))}"
    monkeypatch.setattr(get_settings(), "chroma_collection_name", unique_collection)

    monkeypatch.setattr(vs_mod, "get_embedding_model", lambda: _FakeEmbeddingModel())
    vs_mod.get_vector_store.cache_clear()
    yield
    vs_mod.get_vector_store.cache_clear()


def test_full_chat_flow_upload_then_query(client, auth_headers):
    # 1. Admin uploads a policy document.
    content = (
        b"PROMOTION POLICY\n\n"
        b"Employees become eligible for promotion after 18 months of continuous "
        b"tenure, provided they have a performance rating of at least 3.5."
    )
    files = {"file": ("promotion_policy.txt", io.BytesIO(content), "text/plain")}
    upload = client.post("/api/documents/upload?category=Policy", headers=auth_headers, files=files)
    assert upload.status_code == 201

    # 2. Public chatbot query — mock the Groq call, verify the real retrieval
    #    pipeline actually found and forwarded the right context.
    with patch("app.rag.pipeline.chat_completion") as mock_chat:
        mock_chat.return_value = "Employees are eligible for promotion after 18 months of tenure. [promotion_policy.txt]"
        response = client.post("/api/chat/query", json={"question": "When are employees eligible for promotion?"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert "18 months" in body["answer"]
    assert any(s["document"] == "promotion_policy.txt" for s in body["sources"])

    # Verify the prompt actually sent to Groq contained the retrieved chunk (real grounding, not a stub).
    system_prompt, user_prompt = mock_chat.call_args[0][0], mock_chat.call_args[0][1]
    assert "18 months" in user_prompt
    assert "AI Workforce Assistant" in system_prompt


def test_chat_query_refuses_when_no_documents_ingested(client):
    """No documents uploaded yet -> empty ChromaDB -> refusal, not a fabricated answer."""
    with patch("app.rag.pipeline.chat_completion") as mock_chat:
        response = client.post("/api/chat/query", json={"question": "What is the meaning of life?"})
        mock_chat.assert_not_called()  # LLM should never be called when retrieval is empty

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is False
    assert "could not find sufficient information" in body["answer"]


def test_admin_recommendations_endpoint_requires_auth(client):
    r = client.get("/api/chat/recommendations")
    assert r.status_code == 401


def test_admin_recommendations_uses_admin_decision_mode(client, auth_headers):
    content = b"RETENTION PROGRAMS\n\nStay interviews and compensation review are used for high-risk employees."
    files = {"file": ("retention.txt", io.BytesIO(content), "text/plain")}
    client.post("/api/documents/upload?category=Report", headers=auth_headers, files=files)

    with patch("app.rag.pipeline.chat_completion") as mock_chat:
        mock_chat.return_value = "Recommendation: prioritize stay interviews for high-risk employees."
        response = client.get("/api/chat/recommendations", headers=auth_headers)

    assert response.status_code == 200
    system_prompt = mock_chat.call_args[0][0]
    assert "decision-support" in system_prompt.lower()
