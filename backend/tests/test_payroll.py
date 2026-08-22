def test_payroll_requires_authentication(client):
    response = client.get("/api/payroll/")
    assert response.status_code == 401