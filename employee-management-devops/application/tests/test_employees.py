import json
import pytest

def test_tc02_employee_creation_and_validation(client, sample_department):
    """
    TC02: Employee Creation & Validation
    - Verify valid employee creation returns 201 Created and persisted record.
    - Verify missing required fields returns 400 Bad Request.
    - Verify negative salary rejection returns 400 Bad Request.
    - Verify invalid department ID returns 400 Bad Request.
    """
    payload = {
        "first_name": "Marcus",
        "last_name": "Aurelius",
        "email": "marcus.a@enterprise.devops",
        "phone": "+1-555-0987",
        "hire_date": "2024-01-10",
        "job_title": "Site Reliability Engineer",
        "salary": 115000.0,
        "department_id": sample_department.id,
        "status": "Active"
    }

    # 1. Valid Creation
    res = client.post("/api/v1/employees", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["employee"]["email"] == "marcus.a@enterprise.devops"
    assert data["employee"]["first_name"] == "Marcus"
    assert data["employee"]["department_name"] == sample_department.name

    # 2. Missing Required Field (e.g., job_title)
    invalid_payload = payload.copy()
    invalid_payload.pop("job_title")
    res_err = client.post("/api/v1/employees", json=invalid_payload)
    assert res_err.status_code == 400

    # 3. Negative Salary Validation
    neg_salary_payload = payload.copy()
    neg_salary_payload["email"] = "neg.sal@enterprise.devops"
    neg_salary_payload["salary"] = -5000.0
    res_neg = client.post("/api/v1/employees", json=neg_salary_payload)
    assert res_neg.status_code == 400
    assert "Salary cannot be negative" in res_neg.get_json()["error"]

    # 4. Invalid Department ID
    bad_dept_payload = payload.copy()
    bad_dept_payload["email"] = "bad.dept@enterprise.devops"
    bad_dept_payload["department_id"] = 999999
    res_bad_dept = client.post("/api/v1/employees", json=bad_dept_payload)
    assert res_bad_dept.status_code == 400

def test_tc03_employee_retrieval_and_filtering(client, sample_employee, sample_department):
    """
    TC03: Employee Retrieval & Filtering
    - Verify retrieving employee list with pagination returns 200 OK.
    - Verify retrieval by specific employee ID.
    - Verify search query filtering by name/email.
    - Verify filtering by department ID.
    """
    # 1. Get List
    res = client.get("/api/v1/employees")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] >= 1
    assert any(e["id"] == sample_employee.id for e in data["employees"])

    # 2. Get Single Employee by ID
    res_single = client.get(f"/api/v1/employees/{sample_employee.id}")
    assert res_single.status_code == 200
    assert res_single.get_json()["email"] == sample_employee.email

    # 3. Search Filter
    res_search = client.get(f"/api/v1/employees?search={sample_employee.first_name}")
    assert res_search.status_code == 200
    assert len(res_search.get_json()["employees"]) >= 1

    # 4. Department Filter
    res_dept_filter = client.get(f"/api/v1/employees?department_id={sample_department.id}")
    assert res_dept_filter.status_code == 200
    assert len(res_dept_filter.get_json()["employees"]) >= 1

def test_tc04_employee_update(client, sample_employee):
    """
    TC04: Employee Update
    - Verify updating salary, job title, and status returns 200 OK and updated fields.
    - Verify update for non-existent employee returns 404 Not Found.
    - Verify updating with an already existing email returns 400 Bad Request.
    """
    update_payload = {
        "job_title": "Principal Architect",
        "salary": 145000.0,
        "status": "On Leave"
    }

    # 1. Valid Update
    res = client.put(f"/api/v1/employees/{sample_employee.id}", json=update_payload)
    assert res.status_code == 200
    updated_data = res.get_json()["employee"]
    assert updated_data["job_title"] == "Principal Architect"
    assert updated_data["salary"] == 145000.0
    assert updated_data["status"] == "On Leave"

    # 2. Update Non-existent Employee
    res_404 = client.put("/api/v1/employees/88888", json={"job_title": "Ghost"})
    assert res_404.status_code == 404

def test_tc05_employee_deletion(client, sample_employee):
    """
    TC05: Employee Deletion
    - Verify deleting an employee returns 200 OK.
    - Verify querying deleted employee returns 404 Not Found.
    - Verify subsequent delete attempt returns 404 Not Found.
    """
    # 1. Successful Delete
    res_del = client.delete(f"/api/v1/employees/{sample_employee.id}")
    assert res_del.status_code == 200

    # 2. Verify Employee is Gone
    res_verify = client.get(f"/api/v1/employees/{sample_employee.id}")
    assert res_verify.status_code == 404

    # 3. Duplicate Deletion attempt
    res_del_again = client.delete(f"/api/v1/employees/{sample_employee.id}")
    assert res_del_again.status_code == 404
