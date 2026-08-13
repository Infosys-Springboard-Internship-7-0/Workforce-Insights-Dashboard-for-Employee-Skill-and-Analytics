"""Admin management: only super admins can add/remove admins; safety rails on self-delete/last-admin."""


def test_create_second_admin(client, auth_headers):
    r = client.post(
        "/api/admins",
        headers=auth_headers,
        json={"name": "Second Admin", "email": "second@test.com", "password": "SecondPass123"},
    )
    assert r.status_code == 201
    assert r.json()["email"] == "second@test.com"
    assert r.json()["is_super_admin"] is False


def test_duplicate_email_rejected(client, auth_headers):
    client.post("/api/admins", headers=auth_headers, json={"name": "X", "email": "dup@test.com", "password": "Pass12345"})
    r = client.post("/api/admins", headers=auth_headers, json={"name": "Y", "email": "dup@test.com", "password": "Pass12345"})
    assert r.status_code == 409


def test_non_super_admin_cannot_create_admin(client, auth_headers):
    client.post("/api/admins", headers=auth_headers, json={"name": "Regular", "email": "regular@test.com", "password": "RegularPass123"})
    login = client.post("/api/auth/login", json={"email": "regular@test.com", "password": "RegularPass123"})
    regular_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r = client.post("/api/admins", headers=regular_headers, json={"name": "Z", "email": "z@test.com", "password": "ZPassword123"})
    assert r.status_code == 403


def test_cannot_delete_self(client, auth_headers):
    me = client.get("/api/auth/me", headers=auth_headers).json()
    r = client.delete(f"/api/admins/{me['id']}", headers=auth_headers)
    assert r.status_code == 400


def test_cannot_delete_last_active_admin(client, auth_headers):
    # only the seeded admin exists at this point in a fresh client fixture instance
    me = client.get("/api/auth/me", headers=auth_headers).json()
    others = [a for a in client.get("/api/admins", headers=auth_headers).json() if a["id"] != me["id"]]
    for o in others:
        client.delete(f"/api/admins/{o['id']}", headers=auth_headers)

    r = client.delete(f"/api/admins/{me['id']}", headers=auth_headers)
    assert r.status_code == 400
