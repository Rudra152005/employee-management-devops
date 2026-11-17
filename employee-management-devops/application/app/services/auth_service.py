from app import db
from app.models.user import User

class AuthService:
    @staticmethod
    def authenticate(username, password):
        """Verify user credentials and return user object if valid."""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def register(username, email, password, role="admin"):
        """Register a new user."""
        if User.query.filter((User.username == username) | (User.email == email)).first():
            raise ValueError("Username or Email already registered.")

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)
