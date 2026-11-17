from app.routes.auth import auth_bp
from app.routes.employee import employee_bp
from app.routes.department import department_bp
from app.routes.api import api_bp

__all__ = ["auth_bp", "employee_bp", "department_bp", "api_bp"]
