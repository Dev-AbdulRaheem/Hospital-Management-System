"""Ward and Bed management model."""
from . import db

class Ward(db.Model):
    """Ward tracking: Room Numbers, Bed availability, ICU vs General."""
    __tablename__ = "wards"

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(32), nullable=False)
    bed_number = db.Column(db.String(32), nullable=False)
    ward_type = db.Column(db.String(32), default="General")  # ICU, General, Special
    is_available = db.Column(db.Boolean, default=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=True)

    patient = db.relationship("Patient", backref=db.backref("ward_bed", uselist=False))

    def __repr__(self):
        return f"<Ward {self.room_number} Bed {self.bed_number} ({self.ward_type})>"
