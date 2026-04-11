"""Department model — hospital specialties."""
from . import db


class Department(db.Model):
    """Clinical department (e.g. Cardiology, Neurology)."""
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, default="")

    doctors = db.relationship("Doctor", back_populates="department", lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"
