from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = True if request.form.get("remember") else False

        user = AuthService.authenticate(username, password)
        if user:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("auth.dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    metrics = EmployeeService.get_dashboard_metrics()
    return render_template("dashboard.html", metrics=metrics)
