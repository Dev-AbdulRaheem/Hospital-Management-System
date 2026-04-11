"""Doctor model — staff who treat patients."""
from . import db


class Doctor(db.Model):
    """Doctor account linked to a department."""
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(32), default="")
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, default="")
    specialization = db.Column(db.String(120), default="")
    image_url = db.Column(db.String(255), default="/static/img/doctor-placeholder.jpg")
    consultation_fee = db.Column(db.Float, default=500.0)
    is_active = db.Column(db.Boolean, default=True)
    unavailability_start_date = db.Column(db.Date, nullable=True)
    unavailability_end_date = db.Column(db.Date, nullable=True)
    qualifications = db.Column(db.Text, default="")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    department = db.relationship("Department", back_populates="doctors")

    appointments = db.relationship(
        "Appointment", back_populates="doctor", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Doctor {self.name}>"
