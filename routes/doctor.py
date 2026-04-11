"""Doctor login, dashboard, patient list, and clinical notes."""
from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from models import Appointment, Doctor, Patient, db
from utils.appointment_slots import slot_label
from utils.auth_helpers import doctor_required

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


@doctor_bp.route("/login", methods=["GET", "POST"])
def login():
    """Doctor sign-in (email + password)."""
    if session.get("doctor_id"):
        return redirect(url_for("doctor.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        doc = Doctor.query.filter_by(email=email).first()
        if doc and check_password_hash(doc.password_hash, password):
            session["doctor_id"] = doc.id
            flash("Welcome back.", "success")
            return redirect(url_for("doctor.dashboard"))
        flash("Invalid credentials.", "danger")

    return render_template("doctor/login.html")


@doctor_bp.route("/logout")
def logout():
    session.pop("doctor_id", None)
    flash("Signed out.", "info")
    return redirect(url_for("public.index"))


@doctor_bp.route("/dashboard")
@doctor_required
def dashboard():
    """List upcoming appointments for the logged-in doctor with Workload Stats."""
    doc = Doctor.query.get_or_404(session["doctor_id"])
    from datetime import date, datetime, timedelta

    today = date.today()
    now = datetime.now()

    # Auto-update "Scheduled" to "Missed" logic for doctors too
    missed_appointments = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == "scheduled",
        Appointment.appointment_date <= today,
    ).all()

    for appt in missed_appointments:
        try:
            appt_time_str = appt.time_slot.split('-')[0].strip()
            # Handle both formats: "09:00" and "09:00 - 09:30"
            if ':' not in appt_time_str:
                continue
            # Ensure proper zero-padding for time if needed (e.g. "9:00" -> "09:00")
            if len(appt_time_str.split(':')[0]) == 1:
                appt_time_str = '0' + appt_time_str
            
            appt_datetime = datetime.strptime(f"{appt.appointment_date} {appt_time_str}", "%Y-%m-%d %H:%M")
            if now > appt_datetime + timedelta(hours=6):
                appt.status = "missed"
        except Exception:
            pass
    db.session.commit()

    # Upcoming: today or future
    upcoming = (
        Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= today,
            Appointment.status == "scheduled",
        )
        .order_by(Appointment.appointment_date, Appointment.time_slot)
        .all()
    )

    # Unique patients
    patient_ids = (
        db.session.query(Appointment.patient_id)
        .filter_by(doctor_id=doc.id)
        .distinct()
        .all()
    )
    pats = Patient.query.filter(Patient.id.in_([r[0] for r in patient_ids])).all()

    # Workload Stats
    stats = {
        "pending_today": Appointment.query.filter_by(doctor_id=doc.id, appointment_date=today, status="scheduled").count(),
        "completed_today": Appointment.query.filter_by(doctor_id=doc.id, appointment_date=today, status="completed").count(),
    }

    return render_template(
        "doctor/dashboard.html",
        doctor=doc,
        upcoming=upcoming,
        patients=pats,
        stats=stats,
        slot_label=slot_label,
    )


@doctor_bp.route("/toggle-availability", methods=["POST"])
@doctor_required
def toggle_availability():
    """Toggle doctor's active status (available for booking)."""
    doc = Doctor.query.get_or_404(session["doctor_id"])
    doc.is_active = not doc.is_active
    db.session.commit()
    status = "Available" if doc.is_active else "Unavailable"
    flash(f"Your status is now {status}.", "success")
    return redirect(url_for("doctor.dashboard"))


@doctor_bp.route("/set-unavailability", methods=["POST"])
@doctor_required
def set_unavailability():
    """Set doctor's unavailability date range."""
    doc = Doctor.query.get_or_404(session["doctor_id"])
    from datetime import datetime
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid start date format.", "danger")
            return redirect(url_for("doctor.dashboard"))
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid end date format.", "danger")
            return redirect(url_for("doctor.dashboard"))

    if start_date and end_date and start_date > end_date:
        flash("Start date cannot be after end date.", "danger")
        return redirect(url_for("doctor.dashboard"))

    doc.unavailability_start_date = start_date
    doc.unavailability_end_date = end_date
    db.session.commit()
    flash("Unavailability updated successfully.", "success")
    return redirect(url_for("doctor.dashboard"))


@doctor_bp.route("/patient/<int:patient_id>")
@doctor_required
def patient_detail(patient_id):
    """View patient profile and appointments with this doctor."""
    doc = Doctor.query.get_or_404(session["doctor_id"])
    pat = Patient.query.get_or_404(patient_id)
    from datetime import date
    
    today = date.today()
    all_appts = (
        Appointment.query.filter_by(doctor_id=doc.id, patient_id=patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc())
        .all()
    )
    
    edit_appt_id = request.args.get("edit_appt_id", type=int)
    if edit_appt_id:
        active_appointment = next((a for a in all_appts if a.id == edit_appt_id), None)
    else:
        active_appointment = next((a for a in all_appts if a.appointment_date == today and a.status == 'scheduled'), None)
        if not active_appointment:
            # Pick any scheduled or missed one
            active_appointment = next((a for a in all_appts if a.status in ['scheduled', 'missed']), None)
            
    past_appointments = [a for a in all_appts if a != active_appointment]
    
    if not all_appts:
        flash("No records for this patient under your care.", "warning")
        return redirect(url_for("doctor.dashboard"))
        
    return render_template(
        "doctor/patient_detail.html",
        doctor=doc,
        patient=pat,
        active_appointment=active_appointment,
        past_appointments=past_appointments,
        slot_label=slot_label,
    )


@doctor_bp.route("/appointment/<int:appt_id>/update", methods=["POST"])
@doctor_required
def update_appointment(appt_id):
    """Save EHR data: vitals, diagnosis, prescription, and notes."""
    doc = Doctor.query.get_or_404(session["doctor_id"])
    ap = Appointment.query.get_or_404(appt_id)
    if ap.doctor_id != doc.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("doctor.dashboard"))

    # Vitals
    ap.vitals_bp = request.form.get("vitals_bp", "").strip()
    ap.vitals_temp = request.form.get("vitals_temp", "").strip()
    ap.vitals_weight = request.form.get("vitals_weight", "").strip()
    ap.vitals_heart_rate = request.form.get("vitals_heart_rate", "").strip()
    
    # Clinical Info
    ap.symptoms = request.form.get("symptoms", "").strip()
    ap.diagnosis = request.form.get("diagnosis", "").strip()
    ap.prescription = request.form.get("prescription", "").strip()
    ap.ordered_tests = request.form.get("ordered_tests", "").strip()
    ap.lab_result_link = request.form.get("lab_result_link", "").strip()
    ap.notes = request.form.get("notes", "").strip()
    
    # Status
    status = request.form.get("status", "scheduled").strip()
    if status in ("scheduled", "completed", "cancelled"):
        # Auto-calculate invoice if completing
        if status == "completed":
            # Ensure consultation_fee is used
            base_fee = doc.consultation_fee or 500.0
            test_fee = 0.0
            if ap.ordered_tests:
                tests = [t.strip() for t in ap.ordered_tests.split(",") if t.strip()]
                test_fee = len(tests) * 200.0 # Standard test fee
            ap.invoice_amount = base_fee + test_fee
        ap.status = status
        
    db.session.commit()
    flash("EHR record updated successfully.", "success")
    return redirect(url_for("doctor.patient_detail", patient_id=ap.patient_id))
