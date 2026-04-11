"""Appointment model — scheduling with double-booking prevention."""
from . import db


class Appointment(db.Model):
    """One booking: patient + doctor + date + time slot (unique per doctor)."""
    __tablename__ = "appointments"
    __table_args__ = (
        db.UniqueConstraint(
            "doctor_id", "appointment_date", "time_slot", name="uq_doctor_date_slot"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(8), nullable=False)  # e.g. "09:30"
    status = db.Column(db.String(32), default="scheduled")  # scheduled, completed, cancelled, pending_lab, results_ready
    symptoms = db.Column(db.Text, default="")
    diagnosis = db.Column(db.String(255), default="")
    notes = db.Column(db.Text, default="")
    
    # EHR Vitals
    vitals_bp = db.Column(db.String(20), default="")
    vitals_temp = db.Column(db.String(10), default="")
    vitals_weight = db.Column(db.String(10), default="")
    vitals_heart_rate = db.Column(db.String(10), default="")
    
    # Prescription (JSON format for multiple medicines)
    prescription_json = db.Column(db.Text, default="[]") # JSON string: [{name, dosage, duration, notes}]
    prescription = db.Column(db.Text, default="") # Legacy/Simple view
    
    # Lab Workflow
    ordered_tests = db.Column(db.Text, default="") # List of tests ordered
    lab_result_link = db.Column(db.String(255), default="")
    lab_report_path = db.Column(db.String(255), default="") # Legacy
    
    # Billing
    is_paid = db.Column(db.Boolean, default=False)
    invoice_amount = db.Column(db.Float, default=0.0)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment {self.id} {self.appointment_date} {self.time_slot}>"
