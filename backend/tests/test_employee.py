def test_employee_profile_requires_authentication(client):
    response = client.get("/api/employees/me")
    assert response.status_code == 401