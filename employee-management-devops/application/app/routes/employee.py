import csv
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required
from app.services.employee_service import EmployeeService
from app.services.department_service import DepartmentService

employee_bp = Blueprint("employee", __name__)

@employee_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    department_id = request.args.get("department_id", "", type=str)
    status = request.args.get("status", "", type=str)

    pagination = EmployeeService.get_all(
        search=search,
        department_id=department_id if department_id else None,
        status=status if status else None,
        page=page,
        per_page=10
    )
    departments = DepartmentService.get_all()

    return render_template(
        "employees/index.html",
        employees=pagination.items,
        pagination=pagination,
        departments=departments,
        search=search,
        selected_dept=int(department_id) if department_id and department_id.isdigit() else None,
        selected_status=status
    )

@employee_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    departments = DepartmentService.get_all()
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        hire_date = request.form.get("hire_date")
        job_title = request.form.get("job_title")
        salary = request.form.get("salary")
        department_id = request.form.get("department_id")
        status = request.form.get("status", "Active")

        try:
            EmployeeService.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                hire_date=hire_date,
                job_title=job_title,
                salary=salary,
                department_id=department_id,
                status=status
            )
            flash(f"Employee {first_name} {last_name} added successfully!", "success")
            return redirect(url_for("employee.index"))
        except Exception as e:
            flash(f"Error creating employee: {str(e)}", "danger")

    return render_template("employees/add.html", departments=departments)

@employee_bp.route("/edit/<int:employee_id>", methods=["GET", "POST"])
@login_required
def edit(employee_id):
    employee = EmployeeService.get_by_id(employee_id)
    if not employee:
        flash("Employee not found.", "warning")
        return redirect(url_for("employee.index"))

    departments = DepartmentService.get_all()

    if request.method == "POST":
        try:
            EmployeeService.update(
                employee_id=employee_id,
                first_name=request.form.get("first_name"),
                last_name=request.form.get("last_name"),
                email=request.form.get("email"),
                phone=request.form.get("phone"),
                hire_date=request.form.get("hire_date"),
                job_title=request.form.get("job_title"),
                salary=request.form.get("salary"),
                department_id=request.form.get("department_id"),
                status=request.form.get("status")
            )
            flash(f"Employee record for {employee.full_name} updated successfully!", "success")
            return redirect(url_for("employee.index"))
        except Exception as e:
            flash(f"Error updating employee: {str(e)}", "danger")

    return render_template("employees/edit.html", employee=employee, departments=departments)

@employee_bp.route("/delete/<int:employee_id>", methods=["POST"])
@login_required
def delete(employee_id):
    try:
        EmployeeService.delete(employee_id)
        flash("Employee deleted successfully.", "success")
    except Exception as e:
        flash(f"Failed to delete employee: {str(e)}", "danger")
    return redirect(url_for("employee.index"))

@employee_bp.route("/export/csv")
@login_required
def export_csv():
    employees = EmployeeService.get_all_list()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Hire Date", "Job Title", "Salary", "Status", "Department"])

    for emp in employees:
        writer.writerow([
            emp.id,
            emp.first_name,
            emp.last_name,
            emp.email,
            emp.phone or "",
            emp.hire_date.strftime("%Y-%m-%d"),
            emp.job_title,
            emp.salary,
            emp.status,
            emp.department.name if emp.department else ""
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=employees_export.csv"}
    )
