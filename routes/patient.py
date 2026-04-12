"""Patient registration, login, dashboard, and appointment booking."""
from datetime import date, datetime, timedelta

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import Appointment, Doctor, Patient, db
from utils.appointment_slots import all_time_slots, slot_label
from utils.auth_helpers import patient_required

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


@patient_bp.route("/register", methods=["GET", "POST"])
def register():
    """New patient account."""
    if session.get("patient_id"):
        return redirect(url_for("patient.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()
        dob_s = request.form.get("date_of_birth", "").strip()

        # Validate Name
        if not name:
            flash("Name is required.", "danger")
            return render_template("patient/register.html")

        # Validate Email
        if not email or "@" not in email or "." not in email:
            flash("Valid email is required.", "danger")
            return render_template("patient/register.html")
        if Patient.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return render_template("patient/register.html")

        # Validate Password
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("patient/register.html")

        # Validate Phone Number
        if phone and (not phone.isdigit() or len(phone) != 10):
            flash("Phone number must be exactly 10 digits.", "danger")
            return render_template("patient/register.html")

        # Validate Date of Birth
        dob = None
        if dob_s:
            try:
                dob = datetime.strptime(dob_s, "%Y-%m-%d").date()
                if dob >= date.today():
                    flash("Date of Birth must be in the past.", "danger")
                    return render_template("patient/register.html")
            except ValueError:
                flash("Invalid date of birth format.", "danger")
                return render_template("patient/register.html")

        p = Patient(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            gender=gender,
            address=address,
            date_of_birth=dob,
        )
        db.session.add(p)
        db.session.commit()
        session["patient_id"] = p.id
        flash("Registration successful. Welcome!", "success")
        
        # Check for redirect after registration
        next_url = request.args.get("next")
        doctor_id = request.args.get("doctor_id")
        
        if next_url:
            try:
                if doctor_id:
                    return redirect(url_for(next_url, doctor_id=doctor_id))
                return redirect(url_for(next_url))
            except:
                pass # Fallback to dashboard
            
        return redirect(url_for("patient.dashboard"))

    return render_template("patient/register.html")


@patient_bp.route("/login", methods=["GET", "POST"])
def login():
    """Patient sign-in."""
    if session.get("patient_id"):
        return redirect(url_for("patient.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        p = Patient.query.filter_by(email=email).first()
        if p and check_password_hash(p.password_hash, password):
            session["patient_id"] = p.id
            flash("Signed in successfully.", "success")
            
            # Check for redirect after login
            next_url = request.args.get("next")
            doctor_id = request.args.get("doctor_id")
            
            if next_url:
                try:
                    # If doctor_id is present (for booking), pass it along
                    if doctor_id:
                        return redirect(url_for(next_url, doctor_id=doctor_id))
                    return redirect(url_for(next_url))
                except:
                    pass # Fallback to dashboard if endpoint is invalid
            
            return redirect(url_for("patient.dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("patient/login.html")


@patient_bp.route("/logout")
def logout():
    """Clear patient session."""
    session.pop("patient_id", None)
    flash("You have been signed out.", "info")
    return redirect(url_for("public.login_hub"))


@patient_bp.route("/dashboard")
@patient_required
def dashboard():
    """Patient home: profile summary, upcoming and past appointments."""
    p = Patient.query.get_or_404(session["patient_id"])
    today = date.today()
    now = datetime.now()

    # Auto-update "Scheduled" to "Missed" if 6 hours past appointment time
    # This is a simplified check for demo purposes. A real system would use a background task.
    missed_appointments = Appointment.query.filter(
        Appointment.patient_id == p.id,
        Appointment.status == "scheduled",
        Appointment.appointment_date <= today,
    ).all()

    for appt in missed_appointments:
        try:
            # Combine appointment date and time slot to create a datetime object
            appt_time_str = appt.time_slot.split('-')[0].strip() # e.g., "09:00" from "09:00 - 09:30"
            if ':' not in appt_time_str:
                continue
            # Ensure proper zero-padding for time if needed
            if len(appt_time_str.split(':')[0]) == 1:
                appt_time_str = '0' + appt_time_str
                
            appt_datetime_str = f"{appt.appointment_date} {appt_time_str}"
            appt_datetime = datetime.strptime(appt_datetime_str, "%Y-%m-%d %H:%M")

            # Check if current time is 6 hours past appointment time
            if now > appt_datetime + timedelta(hours=6):
                appt.status = "missed"
        except Exception:
            pass
    db.session.commit()

    upcoming = (
        Appointment.query.filter(
            Appointment.patient_id == p.id,
            Appointment.appointment_date >= today,
            Appointment.status != "cancelled",
            Appointment.status != "missed",
        )
        .order_by(Appointment.appointment_date, Appointment.time_slot)
        .all()
    )
    history = (
        Appointment.query.filter(
            Appointment.patient_id == p.id,
            (Appointment.appointment_date < today) | (Appointment.status == "completed") | (Appointment.status == "missed") | (Appointment.status == "cancelled"),
        )
        .order_by(Appointment.appointment_date.desc())
        .limit(20)
        .all()
    )
    # Quick Stats
    stats = {
        "total_visits": Appointment.query.filter_by(patient_id=p.id, status="completed").count(),
        "next_appt": upcoming[0].appointment_date.strftime('%d %b') if upcoming else 'None',
        "pending_bills": Appointment.query.filter_by(patient_id=p.id, is_paid=False).filter(Appointment.invoice_amount > 0).count()
    }

    return render_template(
        "patient/dashboard.html",
        patient=p,
        upcoming=upcoming,
        history=history,
        stats=stats,
        slot_label=slot_label,
    )


@patient_bp.route("/book", methods=["GET", "POST"])
@patient_required
def book():
    """Book appointment: doctor, date, time — prevents double booking via DB constraint."""
    # Filter doctors: only active ones, and include their unavailability
    active_doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
    
    # Prepare unavailability data for frontend
    doctor_unavailability = {}
    for doc in active_doctors:
        if doc.unavailability_start_date and doc.unavailability_end_date:
            doctor_unavailability[doc.id] = {
                "start": doc.unavailability_start_date.strftime("%Y-%m-%d"),
                "end": doc.unavailability_end_date.strftime("%Y-%m-%d"),
            }

    selected_doctor_id = request.args.get("doctor_id", type=int)

    if request.method == "POST":
        doctor_id = request.form.get("doctor_id", type=int)
        date_s = request.form.get("appointment_date", "").strip()
        time_slot = request.form.get("time_slot", "").strip()

        if not doctor_id or not date_s or not time_slot:
            flash("Please select doctor, date, and time.", "danger")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        try:
            adate = datetime.strptime(date_s, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date.", "danger")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        if adate < date.today():
            flash("Cannot book appointments in the past.", "danger")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        # Check doctor's unavailability for the selected date
        selected_doctor = Doctor.query.get(doctor_id)
        if selected_doctor and selected_doctor.unavailability_start_date and selected_doctor.unavailability_end_date:
            if selected_doctor.unavailability_start_date <= adate <= selected_doctor.unavailability_end_date:
                flash(f"{selected_doctor.name} is unavailable on {adate.strftime('%Y-%m-%d')}.", "danger")
                return redirect(url_for("patient.book", doctor_id=doctor_id))

        if time_slot not in all_time_slots():
            flash("Invalid time slot.", "danger")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        # Double-booking check
        taken = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=adate,
            time_slot=time_slot,
        ).first()
        if taken:
            flash("That slot was just taken. Please choose another time.", "warning")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        ap = Appointment(
            patient_id=session["patient_id"],
            doctor_id=doctor_id,
            appointment_date=adate,
            time_slot=time_slot,
            status="scheduled",
        )
        db.session.add(ap)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not book — slot may be unavailable. Try again.", "danger")
            return redirect(url_for("patient.book", doctor_id=doctor_id))

        flash(
            f"Appointment confirmed for {adate.strftime('%B %d, %Y')} at {slot_label(time_slot)}.",
            "success",
        )
        return redirect(url_for("patient.dashboard"))

    return render_template(
        "patient/book.html", 
        active_doctors=active_doctors, 
        all_slots=all_time_slots(), 
        slot_label=slot_label,
        selected_doctor_id=selected_doctor_id,
        doctor_unavailability=doctor_unavailability
    )


@patient_bp.route("/appointment/<int:appt_id>/pay", methods=["POST"])
@patient_required
def pay_appointment(appt_id):
    """Mock payment: mark appointment as paid."""
    ap = Appointment.query.get_or_404(appt_id)
    if ap.patient_id != session["patient_id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    ap.is_paid = True
    db.session.commit()
    return jsonify({"success": True})


@patient_bp.route("/appointment/<int:appt_id>/cancel", methods=["POST"])
@patient_required
def cancel_appointment(appt_id):
    """Allow patient to cancel their own appointment."""
    ap = Appointment.query.get_or_404(appt_id)
    if ap.patient_id != session["patient_id"]:
        flash("Unauthorized to cancel this appointment.", "danger")
        return redirect(url_for("patient.dashboard"))
    
    if ap.status == "scheduled":
        ap.status = "cancelled"
        db.session.commit()
        flash("Appointment cancelled successfully.", "success")
    else:
        flash(f"Cannot cancel an appointment with status: {ap.status}.", "warning")
        
    return redirect(url_for("patient.dashboard"))


@patient_bp.route("/prescription/<int:appt_id>")
@patient_required
def prescription_receipt(appt_id):
    """Printable receipt view for a prescription."""
    p_id = session["patient_id"]
    ap = Appointment.query.get_or_404(appt_id)
    if ap.patient_id != p_id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("patient.dashboard"))
    
    return render_template("shared/prescription_receipt.html", appt=ap)


@patient_bp.route("/api/available-slots")
@patient_required
def api_available_slots():
    """JSON list of free slots for a doctor on a given date (dynamic booking UI)."""
    doctor_id = request.args.get("doctor_id", type=int)
    date_s = request.args.get("date", "").strip()
    if not doctor_id or not date_s:
        return jsonify({"slots": [], "error": "doctor_id and date required"}), 400
    try:
        adate = datetime.strptime(date_s, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"slots": [], "error": "invalid date"}), 400

    if adate < date.today():
        return jsonify({"slots": [], "message": "past_date"})

    booked = {
        a.time_slot
        for a in Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == adate,
            Appointment.status != "cancelled",
        ).all()
    }
    free = [s for s in all_time_slots() if s not in booked]
    return jsonify(
        {
            "slots": [{"value": s, "label": slot_label(s)} for s in free],
        }
    )
