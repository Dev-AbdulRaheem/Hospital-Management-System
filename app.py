"""
Hospital Management System (HMS) — Flask application entry point.
Registers blueprints, database, and demo seed data.
"""
import os

from flask import Flask

from config import Config
from models import Department, db
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.public import public_bp
from utils.seed import seed_if_empty


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure SQLite instance directory exists
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    db.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        """Expose departments in base template for nav dropdown."""
        from datetime import datetime

        try:
            depts = Department.query.order_by(Department.name).limit(24).all()
        except Exception:
            depts = []
        return {"nav_departments": depts, "current_year": datetime.now().year}

    with app.app_context():
        # db.drop_all() # Uncomment to force schema refresh if needed
        db.create_all()
        seed_if_empty(app)

    return app


# WSGI / `python app.py`
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
