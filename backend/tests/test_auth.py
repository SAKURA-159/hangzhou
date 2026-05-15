def test_register(client):
    resp = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "new@test.com",
        "password": "pass123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["is_admin"] is False
    assert "id" in data


def test_register_duplicate(client):
    client.post("/api/auth/register", json={
        "username": "dup", "email": "dup@test.com", "password": "pass123",
    })
    resp = client.post("/api/auth/register", json={
        "username": "dup", "email": "dup@test.com", "password": "pass123",
    })
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "pass123",
    })
    resp = client.post("/api/auth/login", json={
        "username": "loginuser", "password": "pass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrongpw", "email": "wrong@test.com", "password": "pass123",
    })
    resp = client.post("/api/auth/login", json={
        "username": "wrongpw", "password": "wrongpassword",
    })
    assert resp.status_code == 401
