from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.services.department_service import DepartmentService

department_bp = Blueprint("department", __name__)

@department_bp.route("/")
@login_required
def index():
    departments = DepartmentService.get_all()
    return render_template("departments/index.html", departments=departments)

@department_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        description = request.form.get("description")
        budget = request.form.get("budget", 0)

        try:
            DepartmentService.create(name=name, code=code, description=description, budget=budget)
            flash(f"Department '{name}' created successfully!", "success")
            return redirect(url_for("department.index"))
        except Exception as e:
            flash(f"Error creating department: {str(e)}", "danger")

    return render_template("departments/add.html")

@department_bp.route("/edit/<int:department_id>", methods=["GET", "POST"])
@login_required
def edit(department_id):
    dept = DepartmentService.get_by_id(department_id)
    if not dept:
        flash("Department not found.", "warning")
        return redirect(url_for("department.index"))

    if request.method == "POST":
        try:
            DepartmentService.update(
                department_id=department_id,
                name=request.form.get("name"),
                code=request.form.get("code"),
                description=request.form.get("description"),
                budget=request.form.get("budget")
            )
            flash(f"Department '{dept.name}' updated successfully!", "success")
            return redirect(url_for("department.index"))
        except Exception as e:
            flash(f"Error updating department: {str(e)}", "danger")

    return render_template("departments/edit.html", department=dept)

@department_bp.route("/delete/<int:department_id>", methods=["POST"])
@login_required
def delete(department_id):
    try:
        DepartmentService.delete(department_id)
        flash("Department deleted successfully.", "success")
    except Exception as e:
        flash(f"Failed to delete department: {str(e)}", "danger")
    return redirect(url_for("department.index"))
