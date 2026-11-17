from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService
from app.services.department_service import DepartmentService

api_bp = Blueprint("api", __name__)

# --- Health Check ---
@api_bp.route("/health", methods=["GET"])
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "UP", "database": "CONNECTED"}), 200
    except Exception as e:
        return jsonify({"status": "DOWN", "database": str(e)}), 500

# --- Auth Endpoints ---
@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "employee")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields (username, email, password)"}), 400

    try:
        user = AuthService.register(username, email, password, role)
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = AuthService.authenticate(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "username": user.username})
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "Bearer",
        "user": user.to_dict()
    }), 200

# --- Employee Endpoints ---
@api_bp.route("/employees", methods=["GET"])
def get_employees():
    search = request.args.get("search")
    dept_id = request.args.get("department_id")
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = EmployeeService.get_all(
        search=search,
        department_id=dept_id,
        status=status,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "employees": [e.to_dict() for e in pagination.items]
    }), 200

@api_bp.route("/employees/<int:emp_id>", methods=["GET"])
def get_employee(emp_id):
    emp = EmployeeService.get_by_id(emp_id)
    if not emp:
        return jsonify({"error": f"Employee with ID {emp_id} not found"}), 404
    return jsonify(emp.to_dict()), 200

@api_bp.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json() or {}
    required = ["first_name", "last_name", "email", "hire_date", "job_title", "salary", "department_id"]
    for field in required:
        if field not in data or data[field] is None:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    try:
        emp = EmployeeService.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone"),
            hire_date=data["hire_date"],
            job_title=data["job_title"],
            salary=data["salary"],
            department_id=data["department_id"],
            status=data.get("status", "Active")
        )
        return jsonify({
            "message": "Employee created successfully",
            "employee": emp.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@api_bp.route("/employees/<int:emp_id>", methods=["PUT", "PATCH"])
def update_employee(emp_id):
    data = request.get_json() or {}
    try:
        emp = EmployeeService.update(emp_id, **data)
        return jsonify({
            "message": "Employee updated successfully",
            "employee": emp.to_dict()
        }), 200
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@api_bp.route("/employees/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    try:
        EmployeeService.delete(emp_id)
        return jsonify({"message": f"Employee {emp_id} deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

# --- Department Endpoints ---
@api_bp.route("/departments", methods=["GET"])
def get_departments():
    departments = DepartmentService.get_all()
    return jsonify([d.to_dict() for d in departments]), 200

@api_bp.route("/departments/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    dept = DepartmentService.get_by_id(dept_id)
    if not dept:
        return jsonify({"error": f"Department with ID {dept_id} not found"}), 404
    return jsonify(dept.to_dict()), 200

@api_bp.route("/departments", methods=["POST"])
def create_department():
    data = request.get_json() or {}
    if "name" not in data or "code" not in data:
        return jsonify({"error": "Fields 'name' and 'code' are required"}), 400

    try:
        dept = DepartmentService.create(
            name=data["name"],
            code=data["code"],
            description=data.get("description", ""),
            budget=data.get("budget", 0.0)
        )
        return jsonify({
            "message": "Department created successfully",
            "department": dept.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@api_bp.route("/departments/<int:dept_id>", methods=["PUT", "PATCH"])
def update_department(dept_id):
    data = request.get_json() or {}
    try:
        dept = DepartmentService.update(
            dept_id,
            name=data.get("name"),
            code=data.get("code"),
            description=data.get("description"),
            budget=data.get("budget")
        )
        return jsonify({
            "message": "Department updated successfully",
            "department": dept.to_dict()
        }), 200
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400

@api_bp.route("/departments/<int:dept_id>", methods=["DELETE"])
def delete_department(dept_id):
    try:
        DepartmentService.delete(dept_id)
        return jsonify({"message": f"Department {dept_id} deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

# --- Dashboard & Stats Endpoint ---
@api_bp.route("/stats", methods=["GET"])
def get_stats():
    metrics = EmployeeService.get_dashboard_metrics()
    # Format for JSON response
    return jsonify({
        "total_employees": metrics["total_employees"],
        "active_employees": metrics["active_employees"],
        "total_departments": metrics["total_departments"],
        "average_salary": metrics["average_salary"],
        "department_distribution": {
            "labels": metrics["dept_labels"],
            "counts": metrics["dept_counts"]
        }
    }), 200
