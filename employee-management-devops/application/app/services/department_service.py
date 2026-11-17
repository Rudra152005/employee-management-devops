from app import db
from app.models.department import Department

class DepartmentService:
    @staticmethod
    def get_all():
        """Retrieve all departments ordered by name."""
        return Department.query.order_by(Department.name.asc()).all()

    @staticmethod
    def get_by_id(department_id):
        return Department.query.get(department_id)

    @staticmethod
    def get_by_code(code):
        return Department.query.filter_by(code=code.upper()).first()

    @staticmethod
    def create(name, code, description="", budget=0.0):
        name = name.strip()
        code = code.strip().upper()

        if Department.query.filter((Department.name == name) | (Department.code == code)).first():
            raise ValueError(f"Department with name '{name}' or code '{code}' already exists.")

        dept = Department(
            name=name,
            code=code,
            description=description,
            budget=float(budget or 0.0)
        )
        db.session.add(dept)
        db.session.commit()
        return dept

    @staticmethod
    def update(department_id, name=None, code=None, description=None, budget=None):
        dept = Department.query.get(department_id)
        if not dept:
            raise ValueError("Department not found.")

        if name:
            name = name.strip()
            existing = Department.query.filter(Department.name == name, Department.id != department_id).first()
            if existing:
                raise ValueError(f"Department name '{name}' is already in use.")
            dept.name = name

        if code:
            code = code.strip().upper()
            existing = Department.query.filter(Department.code == code, Department.id != department_id).first()
            if existing:
                raise ValueError(f"Department code '{code}' is already in use.")
            dept.code = code

        if description is not None:
            dept.description = description

        if budget is not None:
            dept.budget = float(budget)

        db.session.commit()
        return dept

    @staticmethod
    def delete(department_id):
        dept = Department.query.get(department_id)
        if not dept:
            raise ValueError("Department not found.")
        db.session.delete(dept)
        db.session.commit()
        return True
