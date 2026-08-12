"""Pytest fixtures: isolated temp SQLite DB + FastAPI TestClient per test."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test_platform.db"
os.environ["DOCUMENTS_DIR"] = f"{_tmpdir}/documents"
os.environ["CHROMA_PERSIST_DIR"] = f"{_tmpdir}/chroma_db"
os.environ["INITIAL_ADMIN_EMAIL"] = "admin@test.com"
os.environ["INITIAL_ADMIN_PASSWORD"] = "TestPassword123"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_token(client):
    response = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "TestPassword123"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
