"""Patient model — registered users."""
from datetime import date
from . import db


class Patient(db.Model):
    """Patient registration and profile."""
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(32), default="")
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), default="")
    address = db.Column(db.Text, default="")

    appointments = db.relationship(
        "Appointment", back_populates="patient", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Patient {self.name}>"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
