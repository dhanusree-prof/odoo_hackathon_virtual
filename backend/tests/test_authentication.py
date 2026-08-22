def test_register_and_login(client):
    payload = {"email": "employee@example.com", "password": "secret123", "full_name": "Test Employee"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    response = client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"]