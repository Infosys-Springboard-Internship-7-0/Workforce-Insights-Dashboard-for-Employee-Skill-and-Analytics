"""Team member and Power BI link CRUD, including that listing is public and mutation is admin-only."""


def test_team_crud_flow(client, auth_headers):
    r = client.post(
        "/api/team",
        headers=auth_headers,
        json={"name": "Jane Doe", "role": "RAG Engineer", "contribution": "Built the RAG pipeline.", "display_order": 1},
    )
    assert r.status_code == 201
    member_id = r.json()["id"]

    r = client.get("/api/team")  # public, no auth
    assert r.status_code == 200
    assert any(m["id"] == member_id for m in r.json())

    r = client.put(f"/api/team/{member_id}", headers=auth_headers, json={"role": "Lead RAG Engineer"})
    assert r.status_code == 200
    assert r.json()["role"] == "Lead RAG Engineer"

    r = client.delete(f"/api/team/{member_id}", headers=auth_headers)
    assert r.status_code == 204

    r = client.get("/api/team")
    assert all(m["id"] != member_id for m in r.json())


def test_team_mutation_requires_auth(client):
    r = client.post("/api/team", json={"name": "X", "role": "Y", "contribution": "Z"})
    assert r.status_code == 401


def test_powerbi_crud_flow(client, auth_headers):
    r = client.post(
        "/api/powerbi",
        headers=auth_headers,
        json={"title": "Attrition Dashboard", "embed_url": "https://app.powerbi.com/view?r=abc123"},
    )
    assert r.status_code == 201
    link_id = r.json()["id"]

    r = client.get("/api/powerbi")  # public
    assert r.status_code == 200
    assert any(link["id"] == link_id for link in r.json())

    r = client.put(f"/api/powerbi/{link_id}", headers=auth_headers, json={"is_active": False})
    assert r.status_code == 200

    r = client.get("/api/powerbi")  # active_only=True by default
    assert all(link["id"] != link_id for link in r.json())

    r = client.get("/api/powerbi?active_only=false")
    assert any(link["id"] == link_id for link in r.json())

    r = client.delete(f"/api/powerbi/{link_id}", headers=auth_headers)
    assert r.status_code == 204
