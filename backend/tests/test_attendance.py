def test_clock_in_requires_authentication(client):
    response = client.post("/api/attendance/clock-in")
    assert response.status_code == 401