def test_leave_requires_authentication(client):
    response = client.get("/api/leaves/")
    assert response.status_code == 401