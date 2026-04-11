"""Admin model — system administrators."""
from . import db


class Admin(db.Model):
    """Admin login (separate from patient/doctor)."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default="Administrator")

    def __repr__(self):
        return f"<Admin {self.username}>"
