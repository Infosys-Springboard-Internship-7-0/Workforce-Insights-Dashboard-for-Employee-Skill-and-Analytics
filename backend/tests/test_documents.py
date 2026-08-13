"""
Document upload/list/update/delete, exercising the real extract -> chunk ->
embed -> ChromaDB pipeline end-to-end through the API (with a fake embedder
patched in so this runs offline, without downloading a real model).
"""

import hashlib
import io

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

    unique_collection = f"test_{abs(hash(request.node.nodeid))}"
    monkeypatch.setattr(get_settings(), "chroma_collection_name", unique_collection)

    monkeypatch.setattr(vs_mod, "get_embedding_model", lambda: _FakeEmbeddingModel())
    vs_mod.get_vector_store.cache_clear()
    yield
    vs_mod.get_vector_store.cache_clear()


def test_upload_txt_document(client, auth_headers):
    content = b"PROMOTION POLICY\n\nEmployees become eligible for promotion after 18 months of tenure."
    files = {"file": ("promotion_policy.txt", io.BytesIO(content), "text/plain")}
    r = client.post("/api/documents/upload?category=Policy", headers=auth_headers, files=files)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["document"]["filename"] == "promotion_policy.txt"
    assert body["chunks_created"] >= 1


def test_upload_rejects_unsupported_extension(client, auth_headers):
    files = {"file": ("malware.exe", io.BytesIO(b"whatever"), "application/octet-stream")}
    r = client.post("/api/documents/upload", headers=auth_headers, files=files)
    assert r.status_code == 400


def test_upload_rejects_empty_file(client, auth_headers):
    files = {"file": ("empty.txt", io.BytesIO(b"   "), "text/plain")}
    r = client.post("/api/documents/upload", headers=auth_headers, files=files)
    assert r.status_code == 422


def test_list_update_delete_document(client, auth_headers):
    content = b"LEAVE POLICY\n\nEmployees accrue 20 days of annual leave per year."
    files = {"file": ("leave_policy.txt", io.BytesIO(content), "text/plain")}
    upload = client.post("/api/documents/upload?category=Policy", headers=auth_headers, files=files)
    doc_id = upload.json()["document"]["id"]

    r = client.get("/api/documents", headers=auth_headers)
    assert any(d["id"] == doc_id for d in r.json())

    r = client.put(f"/api/documents/{doc_id}", headers=auth_headers, json={"category": "HR Policy"})
    assert r.status_code == 200
    assert r.json()["category"] == "HR Policy"

    r = client.delete(f"/api/documents/{doc_id}", headers=auth_headers)
    assert r.status_code == 204

    r = client.get("/api/documents", headers=auth_headers)
    assert all(d["id"] != doc_id for d in r.json())


def test_documents_require_auth(client):
    r = client.get("/api/documents")
    assert r.status_code == 401


def test_upload_csv_creates_dataset_visible_in_data_viewer(client, auth_headers):
    content = b"employee_code,department,attrition_risk\nEMP0001,Engineering,Low\nEMP0002,Sales,High\n"
    files = {"file": ("workforce.csv", io.BytesIO(content), "text/csv")}
    upload = client.post("/api/documents/upload?category=Dataset", headers=auth_headers, files=files)
    assert upload.status_code == 201
    doc_id = upload.json()["document"]["id"]

    r = client.get("/api/data-viewer/datasets", headers=auth_headers)
    assert any(d["id"] == doc_id for d in r.json())

    r = client.get(f"/api/data-viewer/datasets/{doc_id}", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["columns"] == ["employee_code", "department", "attrition_risk"]
    assert body["total_rows"] == 2
    assert body["rows"][0]["employee_code"] == "EMP0001"
