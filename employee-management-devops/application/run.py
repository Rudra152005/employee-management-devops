import os
import sys
from datetime import date
from app import create_app, db
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee

config_mode = os.getenv("FLASK_ENV", "development")
app = create_app(config_mode)

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

def seed_data():
    with app.app_context():
        db.create_all()

        # Seed Admin User if not exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", email="admin@enterprise.devops", role="admin")
            admin.set_password("Admin@12345")
            db.session.add(admin)
            print("Created default admin user (admin / Admin@12345)")

        # Seed Departments
        dept_data = [
            {"name": "Engineering", "code": "ENG", "description": "Software & DevOps Infrastructure", "budget": 500000.0},
            {"name": "Human Resources", "code": "HR", "description": "Talent acquisition & people ops", "budget": 150000.0},
            {"name": "Finance", "code": "FIN", "description": "Financial planning & analysis", "budget": 250000.0},
            {"name": "Marketing", "code": "MKT", "description": "Brand & digital marketing", "budget": 180000.0},
        ]
        departments = {}
        for d in dept_data:
            existing = Department.query.filter_by(code=d["code"]).first()
            if not existing:
                dept = Department(name=d["name"], code=d["code"], description=d["description"], budget=d["budget"])
                db.session.add(dept)
                db.session.flush()
                departments[d["code"]] = dept
            else:
                departments[d["code"]] = existing

        # Seed Sample Employees
        if Employee.query.count() == 0:
            sample_emps = [
                {
                    "first_name": "Devin", "last_name": "Vance", "email": "devin.vance@enterprise.io",
                    "phone": "+1-555-0101", "hire_date": date(2023, 1, 15), "job_title": "Lead DevOps Engineer",
                    "salary": 135000.0, "status": "Active", "dept_code": "ENG"
                },
                {
                    "first_name": "Sarah", "last_name": "Connor", "email": "sarah.connor@enterprise.io",
                    "phone": "+1-555-0102", "hire_date": date(2023, 4, 1), "job_title": "Site Reliability Engineer",
                    "salary": 120000.0, "status": "Active", "dept_code": "ENG"
                },
                {
                    "first_name": "Marcus", "last_name": "Brody", "email": "marcus.brody@enterprise.io",
                    "phone": "+1-555-0103", "hire_date": date(2022, 11, 20), "job_title": "HR Director",
                    "salary": 95000.0, "status": "Active", "dept_code": "HR"
                },
                {
                    "first_name": "Elena", "last_name": "Rostova", "email": "elena.rostova@enterprise.io",
                    "phone": "+1-555-0104", "hire_date": date(2024, 2, 10), "job_title": "Financial Analyst",
                    "salary": 88000.0, "status": "Active", "dept_code": "FIN"
                },
                {
                    "first_name": "Alex", "last_name": "Mercer", "email": "alex.mercer@enterprise.io",
                    "phone": "+1-555-0105", "hire_date": date(2024, 5, 18), "job_title": "Growth Marketing Lead",
                    "salary": 92000.0, "status": "On Leave", "dept_code": "MKT"
                }
            ]
            for emp in sample_emps:
                dept = departments.get(emp["dept_code"])
                if dept:
                    new_emp = Employee(
                        first_name=emp["first_name"],
                        last_name=emp["last_name"],
                        email=emp["email"],
                        phone=emp["phone"],
                        hire_date=emp["hire_date"],
                        job_title=emp["job_title"],
                        salary=emp["salary"],
                        status=emp["status"],
                        department_id=dept.id
                    )
                    db.session.add(new_emp)

        db.session.commit()
        print("Database seeded with sample data successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "init-db":
            init_db()
        elif cmd == "seed":
            seed_data()
        else:
            print(f"Unknown command: {cmd}. Available: init-db, seed")
    else:
        # Automatically create tables on start if not in test
        with app.app_context():
            db.create_all()
            # If no admin, seed default admin
            if not User.query.filter_by(username="admin").first():
                seed_data()

        port = int(os.getenv("PORT", 5000))
        host = os.getenv("HOST", "0.0.0.0")
        app.run(host=host, port=port)
