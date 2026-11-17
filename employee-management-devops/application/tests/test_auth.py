import json
import pytest
from app.models.user import User

def test_tc01_user_authentication_and_jwt(client, sample_user):
    """
    TC01: User Authentication & JWT Token Generation
    - Verify successful login with correct credentials returns 200 and JWT access token.
    - Verify failed login with invalid credentials returns 401 Unauthorized.
    - Verify registration of new user returns 201 Created.
    - Verify registration with duplicate email/username returns 400 Bad Request.
    """
    # 1. Successful API Login
    res = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "AdminSecure!2026"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["username"] == "testadmin"

    # 2. Invalid Password
    res_invalid = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "WrongPassword999"
    })
    assert res_invalid.status_code == 401
    assert "Invalid credentials" in res_invalid.get_json()["error"]

    # 3. Non-existent User
    res_none = client.post("/api/v1/auth/login", json={
        "username": "ghost_user",
        "password": "Password123"
    })
    assert res_none.status_code == 401

    # 4. User Registration
    res_reg = client.post("/api/v1/auth/register", json={
        "username": "devops_lead",
        "email": "lead@devops.internal",
        "password": "LeadPassword!123",
        "role": "admin"
    })
    assert res_reg.status_code == 201
    assert res_reg.get_json()["user"]["username"] == "devops_lead"

    # 5. Duplicate Registration Check
    res_dup = client.post("/api/v1/auth/register", json={
        "username": "devops_lead",
        "email": "lead@devops.internal",
        "password": "AnotherPassword"
    })
    assert res_dup.status_code == 400
