import json
import pytest
from app.models.department import Department
from app.models.employee import Employee

def test_tc06_department_management_crud(client):
    """
    TC06: Department Management CRUD
    - Verify creating department returns 201 Created.
    - Verify listing departments returns 200 OK.
    - Verify updating department budget and description returns 200 OK.
    - Verify duplicate department code returns 400 Bad Request.
    """
    # 1. Create Department
    create_payload = {
        "name": "Cybersecurity Operations",
        "code": "CYBER",
        "description": "Information security and SOC",
        "budget": 350000.0
    }
    res = client.post("/api/v1/departments", json=create_payload)
    assert res.status_code == 201
    dept_id = res.get_json()["department"]["id"]

    # 2. List Departments
    res_list = client.get("/api/v1/departments")
    assert res_list.status_code == 200
    assert any(d["code"] == "CYBER" for d in res_list.get_json())

    # 3. Update Department
    update_payload = {
        "budget": 420000.0,
        "description": "SOC, Threat Hunting, and Compliance"
    }
    res_update = client.put(f"/api/v1/departments/{dept_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.get_json()["department"]["budget"] == 420000.0

    # 4. Duplicate Code Conflict
    res_dup = client.post("/api/v1/departments", json={
        "name": "Different Name",
        "code": "CYBER"
    })
    assert res_dup.status_code == 400

def test_tc07_database_integrity_and_constraints(client, sample_department, sample_employee):
    """
    TC07: Database Integrity & Foreign Key Constraints
    - Verify foreign key integrity when department has associated employees.
    - Verify cascade behavior or cleanup upon department deletion.
    - Verify unique email constraint prevents creating two employees with same email.
    """
    # 1. Verify Employee is tied to Department
    assert sample_employee.department_id == sample_department.id

    # 2. Try to create duplicate employee email under same or different department
    dup_payload = {
        "first_name": "Clone",
        "last_name": "Worker",
        "email": sample_employee.email, # duplicate email!
        "hire_date": "2024-02-01",
        "job_title": "Tester",
        "salary": 70000.0,
        "department_id": sample_department.id
    }
    res_dup_email = client.post("/api/v1/employees", json=dup_payload)
    assert res_dup_email.status_code == 400
    assert "already exists" in res_dup_email.get_json()["error"]

    # 3. Department Deletion & Employee Cascade verification
    dept_id = sample_department.id
    emp_id = sample_employee.id

    res_del_dept = client.delete(f"/api/v1/departments/{dept_id}")
    assert res_del_dept.status_code == 200

    # Confirm employee was cascaded or removed
    res_check_emp = client.get(f"/api/v1/employees/{emp_id}")
    assert res_check_emp.status_code == 404
