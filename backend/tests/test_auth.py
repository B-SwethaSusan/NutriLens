def test_signup_login_and_me(client):
    signup = client.post("/api/auth/signup", json={"email": "user@example.com", "password": "password123", "full_name": "Test User"})
    assert signup.status_code == 201
    token = signup.json()["access_token"]
    assert signup.json()["user"]["email"] == "user@example.com"

    login = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert login.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Test User"


def test_invalid_login_is_rejected(client):
    client.post("/api/auth/signup", json={"email": "user@example.com", "password": "password123"})
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrong-password"})
    assert response.status_code == 401
