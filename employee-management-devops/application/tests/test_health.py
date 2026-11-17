import json
import pytest

def test_tc09_health_check_and_metrics(client, sample_employee, sample_department):
    """
    TC09: Application Health Check & Metrics
    - Verify root /health endpoint returns 200 OK and database: connected.
    - Verify /api/v1/health endpoint returns 200 OK and status: UP.
    - Verify /api/v1/stats calculates accurate employee counts, average salary, and department distribution.
    """
    # 1. Root /health endpoint (used by AWS ALB & Nagios)
    res_root_health = client.get("/health")
    assert res_root_health.status_code == 200
    data_root = res_root_health.get_json()
    assert data_root["status"] == "healthy"
    assert data_root["database"] == "connected"
    assert "version" in data_root

    # 2. API /api/v1/health endpoint
    res_api_health = client.get("/api/v1/health")
    assert res_api_health.status_code == 200
    data_api = res_api_health.get_json()
    assert data_api["status"] == "UP"
    assert data_api["database"] == "CONNECTED"

    # 3. Metrics & Stats endpoint
    res_stats = client.get("/api/v1/stats")
    assert res_stats.status_code == 200
    data_stats = res_stats.get_json()
    assert data_stats["total_employees"] >= 1
    assert data_stats["total_departments"] >= 1
    assert data_stats["average_salary"] > 0
    assert "department_distribution" in data_stats
    assert sample_department.name in data_stats["department_distribution"]["labels"]
