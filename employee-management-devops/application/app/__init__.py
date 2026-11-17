from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app(config_name="development"):
    """Application factory for Employee Management System."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Health check route (used by AWS ALB & Nagios)
    @app.route("/health")
    def health_check():
        try:
            # Check DB connectivity
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            return jsonify({
                "status": "unhealthy",
                "database": db_status
            }), 500

        return jsonify({
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0",
            "environment": config_name
        }), 200

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.employee import employee_bp
    from app.routes.department import department_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp, url_prefix="/employees")
    app.register_blueprint(department_bp, url_prefix="/departments")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_title="404 - Page Not Found", error_message="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("base.html", error_title="500 - Server Error", error_message="An internal server error occurred."), 500

    return app
