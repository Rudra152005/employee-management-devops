from datetime import datetime
from sqlalchemy import func
from app import db
from app.models.employee import Employee
from app.models.department import Department

class EmployeeService:
    @staticmethod
    def get_all(search=None, department_id=None, status=None, page=1, per_page=10):
        query = Employee.query.join(Department)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Employee.first_name.ilike(search_term)) |
                (Employee.last_name.ilike(search_term)) |
                (Employee.email.ilike(search_term)) |
                (Employee.job_title.ilike(search_term))
            )

        if department_id:
            query = query.filter(Employee.department_id == int(department_id))

        if status:
            query = query.filter(Employee.status == status)

        query = query.order_by(Employee.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_list():
        return Employee.query.order_by(Employee.last_name.asc()).all()

    @staticmethod
    def get_by_id(employee_id):
        return Employee.query.get(employee_id)

    @staticmethod
    def get_by_email(email):
        return Employee.query.filter_by(email=email.strip().lower()).first()

    @staticmethod
    def create(first_name, last_name, email, phone, hire_date, job_title, salary, department_id, status="Active"):
        email = email.strip().lower()

        # Validation
        if Employee.query.filter_by(email=email).first():
            raise ValueError(f"An employee with email '{email}' already exists.")

        dept = Department.query.get(int(department_id))
        if not dept:
            raise ValueError(f"Department ID {department_id} does not exist.")

        if isinstance(hire_date, str):
            hire_date = datetime.strptime(hire_date, "%Y-%m-%d").date()

        salary = float(salary)
        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        emp = Employee(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            phone=phone.strip() if phone else None,
            hire_date=hire_date,
            job_title=job_title.strip(),
            salary=salary,
            status=status,
            department_id=dept.id
        )
        db.session.add(emp)
        db.session.commit()
        return emp

    @staticmethod
    def update(employee_id, **kwargs):
        emp = Employee.query.get(employee_id)
        if not emp:
            raise ValueError("Employee not found.")

        if "email" in kwargs and kwargs["email"]:
            new_email = kwargs["email"].strip().lower()
            existing = Employee.query.filter(Employee.email == new_email, Employee.id != employee_id).first()
            if existing:
                raise ValueError(f"Email '{new_email}' is already in use by another employee.")
            emp.email = new_email

        if "department_id" in kwargs and kwargs["department_id"]:
            dept = Department.query.get(int(kwargs["department_id"]))
            if not dept:
                raise ValueError("Selected department does not exist.")
            emp.department_id = dept.id

        if "hire_date" in kwargs and kwargs["hire_date"]:
            if isinstance(kwargs["hire_date"], str):
                emp.hire_date = datetime.strptime(kwargs["hire_date"], "%Y-%m-%d").date()
            else:
                emp.hire_date = kwargs["hire_date"]

        if "salary" in kwargs and kwargs["salary"] is not None:
            sal = float(kwargs["salary"])
            if sal < 0:
                raise ValueError("Salary cannot be negative.")
            emp.salary = sal

        for field in ["first_name", "last_name", "phone", "job_title", "status"]:
            if field in kwargs and kwargs[field] is not None:
                setattr(emp, field, kwargs[field].strip() if isinstance(kwargs[field], str) else kwargs[field])

        db.session.commit()
        return emp

    @staticmethod
    def delete(employee_id):
        emp = Employee.query.get(employee_id)
        if not emp:
            raise ValueError("Employee not found.")
        db.session.delete(emp)
        db.session.commit()
        return True

    @staticmethod
    def get_dashboard_metrics():
        """Aggregates metrics for the executive dashboard and charts."""
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status="Active").count()
        total_departments = Department.query.count()
        avg_salary = db.session.query(func.avg(Employee.salary)).scalar() or 0.0

        # Department distribution
        dept_distribution = (
            db.session.query(Department.name, func.count(Employee.id))
            .outerjoin(Employee)
            .group_by(Department.name)
            .all()
        )

        dept_labels = [d[0] for d in dept_distribution]
        dept_counts = [d[1] for d in dept_distribution]

        # Recent hires
        recent_hires = Employee.query.order_by(Employee.hire_date.desc()).limit(5).all()

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_departments": total_departments,
            "average_salary": round(avg_salary, 2),
            "dept_labels": dept_labels,
            "dept_counts": dept_counts,
            "recent_hires": recent_hires
        }
