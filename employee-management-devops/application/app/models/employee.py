from datetime import datetime
from app import db

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.Date, nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Active") # Active, On Leave, Terminated
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to department
    department = db.relationship("Department", back_populates="employees")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "hire_date": self.hire_date.strftime("%Y-%m-%d") if self.hire_date else None,
            "job_title": self.job_title,
            "salary": self.salary,
            "status": self.status,
            "department_id": self.department_id,
            "department_name": self.department.name if self.department else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Employee {self.full_name} ({self.job_title})>"
