"""SQLAlchemy models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .department import Department  # noqa: E402
from .doctor import Doctor  # noqa: E402
from .patient import Patient  # noqa: E402
from .appointment import Appointment  # noqa: E402
from .admin import Admin  # noqa: E402
from .ward import Ward  # noqa: E402

__all__ = ["db", "Department", "Doctor", "Patient", "Appointment", "Admin", "Ward"]
