import json
import pytest

def test_tc08_api_error_handling_and_status_codes(client):
    """
    TC08: API Error Handling & Status Codes
    - Verify 404 Not Found for non-existent routes.
    - Verify 405 Method Not Allowed when using invalid HTTP verbs.
    - Verify 400 Bad Request for malformed requests.
    """
    # 1. 404 on invalid API endpoint
    res_404 = client.get("/api/v1/non_existent_route")
    assert res_404.status_code == 404

    # 2. 405 Method Not Allowed (e.g. POST to GET-only stats endpoint)
    res_405 = client.post("/api/v1/stats", json={"data": 123})
    assert res_405.status_code == 405

    # 3. 400 Bad Request on empty employee payload
    res_400 = client.post("/api/v1/employees", json={})
    assert res_400.status_code == 400
    assert "Missing required field" in res_400.get_json()["error"]
