import pytest
from datetime import date
from app import create_app, db
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee

@pytest.fixture(scope="session")
def app():
    """Create test application instance."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

@pytest.fixture(scope="function")
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture(scope="function")
def db_session(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        db.session.rollback()
        # Clean existing tables
        Employee.query.delete()
        Department.query.delete()
        User.query.delete()
        db.session.commit()

        yield db.session

        db.session.rollback()

@pytest.fixture
def sample_user(db_session):
    """Create a sample admin user."""
    user = User(username="testadmin", email="testadmin@enterprise.devops", role="admin")
    user.set_password("AdminSecure!2026")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_department(db_session):
    """Create a sample department."""
    dept = Department(
        name="Platform Engineering",
        code="PLATFORM",
        description="Cloud, Kubernetes, and CI/CD pipelines",
        budget=450000.0
    )
    db_session.add(dept)
    db_session.commit()
    return dept

@pytest.fixture
def sample_employee(db_session, sample_department):
    """Create a sample employee."""
    emp = Employee(
        first_name="Alice",
        last_name="Johnson",
        email="alice.j@enterprise.devops",
        phone="+1-555-0155",
        hire_date=date(2023, 6, 1),
        job_title="Lead Cloud Engineer",
        salary=125000.0,
        status="Active",
        department_id=sample_department.id
    )
    db_session.add(emp)
    db_session.commit()
    return emp
