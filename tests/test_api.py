def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["docs"] == "/docs"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert "uptime_seconds" in body


def test_liveness(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_seeded_users(client):
    r = client.get("/users", params={"limit": 100})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 25
    assert len(body["items"]) == 25


def test_pagination_and_search(client):
    r = client.get("/users", params={"skip": 5, "limit": 5})
    assert r.status_code == 200
    assert len(r.json()["items"]) == 5

    r = client.get("/users", params={"q": "@example.com"})
    assert r.json()["total"] == 25


def test_crud_flow(client):
    # create
    r = client.post("/users", json={"name": "Test User", "email": "Test.User@Example.com", "age": 30})
    assert r.status_code == 201, r.text
    user = r.json()
    uid = user["id"]
    assert user["email"] == "test.user@example.com"
    assert user["is_active"] is True

    # duplicate email
    r = client.post("/users", json={"name": "Copy", "email": "test.user@example.com"})
    assert r.status_code == 409

    # read
    r = client.get(f"/users/{uid}")
    assert r.status_code == 200
    assert r.json()["name"] == "Test User"

    # partial update
    r = client.patch(f"/users/{uid}", json={"age": 31, "is_active": False})
    assert r.status_code == 200
    assert r.json()["age"] == 31
    assert r.json()["is_active"] is False
    assert r.json()["name"] == "Test User"

    # full replace
    r = client.put(f"/users/{uid}", json={"name": "Replaced", "email": "replaced@example.com"})
    assert r.status_code == 200
    assert r.json()["name"] == "Replaced"
    assert r.json()["age"] is None

    # delete
    r = client.delete(f"/users/{uid}")
    assert r.status_code == 204
    assert client.get(f"/users/{uid}").status_code == 404
    assert client.delete(f"/users/{uid}").status_code == 404


def test_validation_errors(client):
    assert client.post("/users", json={"name": "X", "email": "not-an-email"}).status_code == 422
    assert client.post("/users", json={"name": "", "email": "a@example.com"}).status_code == 422
    assert client.post("/users", json={"name": "X", "email": "b@example.com", "age": -1}).status_code == 422
    assert client.patch("/users/1", json={"name": None}).status_code == 422


def test_patch_email_conflict(client):
    first, second = client.get("/users", params={"limit": 2}).json()["items"]
    r = client.patch(f"/users/{second['id']}", json={"email": first["email"]})
    assert r.status_code == 409
