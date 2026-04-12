"""Administrator: CRUD for patients, doctors, appointments, and simple reports."""
from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from models import Appointment, Admin, Department, Doctor, Patient, Ward, db
from utils.appointment_slots import all_time_slots, slot_label
from utils.auth_helpers import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin username + password."""
    if session.get("admin_id"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        from werkzeug.security import check_password_hash

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["admin_id"] = user.id
            flash("Signed in as administrator.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_id", None)
    flash("Signed out.", "info")
    return redirect(url_for("public.login_hub"))


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Overview counts and quick links with Charts and Activity."""
    from sqlalchemy import func
    
    stats = {
        "patients": Patient.query.count(),
        "doctors": Doctor.query.count(),
        "appointments": Appointment.query.count(),
        "today": Appointment.query.filter_by(appointment_date=date.today()).count(),
    }
    
    # Chart 1: Department Distribution (Pie Chart)
    dept_dist = db.session.query(Department.name, func.count(Doctor.id))\
        .outerjoin(Doctor, Doctor.department_id == Department.id)\
        .group_by(Department.id, Department.name).all()
    
    chart_labels = [d[0] for d in dept_dist]
    chart_values = [d[1] for d in dept_dist]
    
    # Recent Activity: Last 5 appointments
    recent_appts = Appointment.query.order_by(Appointment.id.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html", 
        stats=stats, 
        chart_labels=chart_labels, 
        chart_values=chart_values,
        recent_appts=recent_appts,
        slot_label=slot_label
    )


# --- Patients CRUD ---


@admin_bp.route("/patients")
@admin_required
def patients_list():
    q = request.args.get("q", "").strip()
    query = Patient.query
    if q:
        query = query.filter(db.or_(Patient.name.ilike(f"%{q}%"), Patient.phone.ilike(f"%{q}%")))
    rows = query.order_by(Patient.name).all()
    return render_template("admin/patients.html", patients=rows, search_query=q)


@admin_bp.route("/patients/add", methods=["GET", "POST"])
@admin_required
def patients_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "") or "patient123"
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()
        dob_s = request.form.get("date_of_birth", "").strip()
        if not name or not email:
            flash("Name and email are required.", "danger")
            return render_template("admin/patient_form.html", patient=None)
        if Patient.query.filter_by(email=email).first():
            flash("Email already in use.", "danger")
            return render_template("admin/patient_form.html", patient=None)
        dob = None
        if dob_s:
            try:
                dob = datetime.strptime(dob_s, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date.", "danger")
                return render_template("admin/patient_form.html", patient=None)
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
        flash("Patient created.", "success")
        return redirect(url_for("admin.patients_list"))
    return render_template("admin/patient_form.html", patient=None)


@admin_bp.route("/patients/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def patients_edit(pid):
    p = Patient.query.get_or_404(pid)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()
        dob_s = request.form.get("date_of_birth", "").strip()
        if not name or not email:
            flash("Name and email are required.", "danger")
            return render_template("admin/patient_form.html", patient=p)
        other = Patient.query.filter(Patient.email == email, Patient.id != p.id).first()
        if other:
            flash("Email already in use.", "danger")
            return render_template("admin/patient_form.html", patient=p)
        p.name = name
        p.email = email
        if password:
            p.password_hash = generate_password_hash(password)
        p.phone = phone
        p.gender = gender
        p.address = address
        if dob_s:
            try:
                p.date_of_birth = datetime.strptime(dob_s, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date — other fields saved.", "warning")
        db.session.commit()
        flash("Patient updated.", "success")
        return redirect(url_for("admin.patients_list"))
    return render_template("admin/patient_form.html", patient=p)


@admin_bp.route("/patients/<int:pid>/delete", methods=["POST"])
@admin_required
def patients_delete(pid):
    p = Patient.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash("Patient deleted.", "info")
    return redirect(url_for("admin.patients_list"))


# --- Doctors CRUD ---


@admin_bp.route("/doctors")
@admin_required
def doctors_list():
    """List doctors with search and department filter."""
    q = request.args.get("q", "").strip()
    dept_id = request.args.get("dept", type=int)
    
    query = Doctor.query.join(Department)
    
    if q:
        query = query.filter(Doctor.name.ilike(f"%{q}%"))
    if dept_id:
        query = query.filter(Doctor.department_id == dept_id)
        
    rows = query.order_by(Doctor.name).all()
    departments = Department.query.order_by(Department.name).all()
    
    return render_template("admin/doctors.html", doctors=rows, departments=departments, search_query=q, selected_dept=dept_id)


@admin_bp.route("/doctors/add", methods=["GET", "POST"])
@admin_required
def doctors_add():
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "") or "doctor123"
        phone = request.form.get("phone", "").strip()
        dept_id = request.form.get("department_id", type=int)
        years = request.form.get("experience_years", type=int) or 0
        fee = request.form.get("consultation_fee", type=float) or 500.0
        bio = request.form.get("bio", "").strip()
        qualifications = request.form.get("qualifications", "").strip()
        unavail_start_str = request.form.get("unavailability_start_date", "").strip()
        unavail_end_str = request.form.get("unavailability_end_date", "").strip()

        unavail_start = None
        if unavail_start_str:
            try:
                unavail_start = datetime.strptime(unavail_start_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid unavailability start date format.", "danger")
                return render_template("admin/doctor_form.html", doctor=None, departments=departments)
        
        unavail_end = None
        if unavail_end_str:
            try:
                unavail_end = datetime.strptime(unavail_end_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid unavailability end date format.", "danger")
                return render_template("admin/doctor_form.html", doctor=None, departments=departments)

        if unavail_start and unavail_end and unavail_start > unavail_end:
            flash("Unavailability start date cannot be after end date.", "danger")
            return render_template("admin/doctor_form.html", doctor=None, departments=departments)

        if not name or not email or not dept_id:
            flash("Name, email, and department are required.", "danger")
            return render_template("admin/doctor_form.html", doctor=None, departments=departments)
        if Doctor.query.filter_by(email=email).first():
            flash("Email already in use.", "danger")
            return render_template("admin/doctor_form.html", doctor=None, departments=departments)
        d = Doctor(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            department_id=dept_id,
            experience_years=years,
            consultation_fee=fee,
            bio=bio,
            qualifications=qualifications,
            unavailability_start_date=unavail_start,
            unavailability_end_date=unavail_end,
            image_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}"
        )
        db.session.add(d)
        db.session.commit()
        flash("Doctor created.", "success")
        return redirect(url_for("admin.doctors_list"))
    return render_template("admin/doctor_form.html", doctor=None, departments=departments)


@admin_bp.route("/doctors/<int:did>/edit", methods=["GET", "POST"])
@admin_required
def doctors_edit(did):
    doc = Doctor.query.get_or_404(did)
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()
        dept_id = request.form.get("department_id", type=int)
        years = request.form.get("experience_years", type=int) or 0
        fee = request.form.get("consultation_fee", type=float) or 500.0
        bio = request.form.get("bio", "").strip()
        qualifications = request.form.get("qualifications", "").strip()
        unavail_start_str = request.form.get("unavailability_start_date", "").strip()
        unavail_end_str = request.form.get("unavailability_end_date", "").strip()

        unavail_start = None
        if unavail_start_str:
            try:
                unavail_start = datetime.strptime(unavail_start_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid unavailability start date format.", "danger")
                return render_template("admin/doctor_form.html", doctor=doc, departments=departments)
        
        unavail_end = None
        if unavail_end_str:
            try:
                unavail_end = datetime.strptime(unavail_end_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid unavailability end date format.", "danger")
                return render_template("admin/doctor_form.html", doctor=doc, departments=departments)

        if unavail_start and unavail_end and unavail_start > unavail_end:
            flash("Unavailability start date cannot be after end date.", "danger")
            return render_template("admin/doctor_form.html", doctor=doc, departments=departments)

        if not name or not email or not dept_id:
            flash("Name, email, and department are required.", "danger")
            return render_template("admin/doctor_form.html", doctor=doc, departments=departments)
        other = Doctor.query.filter(Doctor.email == email, Doctor.id != doc.id).first()
        if other:
            flash("Email already in use.", "danger")
            return render_template("admin/doctor_form.html", doctor=doc, departments=departments)
        doc.name = name
        doc.email = email
        if password:
            doc.password_hash = generate_password_hash(password)
        doc.phone = phone
        doc.department_id = dept_id
        doc.experience_years = years
        doc.consultation_fee = fee
        doc.bio = bio
        doc.qualifications = qualifications
        doc.unavailability_start_date = unavail_start
        doc.unavailability_end_date = unavail_end
        db.session.commit()
        flash("Doctor updated.", "success")
        return redirect(url_for("admin.doctors_list"))
    return render_template("admin/doctor_form.html", doctor=doc, departments=departments)


@admin_bp.route("/doctors/<int:did>/delete", methods=["POST"])
@admin_required
def doctors_delete(did):
    doc = Doctor.query.get_or_404(did)
    db.session.delete(doc)
    db.session.commit()
    flash("Doctor removed.", "info")
    return redirect(url_for("admin.doctors_list"))


# --- Appointments ---


@admin_bp.route("/appointments")
@admin_required
def appointments_list():
    rows = (
        Appointment.query.join(Patient).join(Doctor)
        .order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc())
        .all()
    )
    return render_template(
        "admin/appointments.html",
        appointments=rows,
        slot_label=slot_label,
        all_slots=all_time_slots(),
    )


@admin_bp.route("/appointments/<int:aid>/edit", methods=["GET", "POST"])
@admin_required
def appointments_edit(aid):
    ap = Appointment.query.get_or_404(aid)
    doctors = Doctor.query.order_by(Doctor.name).all()
    patients = Patient.query.order_by(Patient.name).all()
    if request.method == "POST":
        ap.patient_id = request.form.get("patient_id", type=int)
        ap.doctor_id = request.form.get("doctor_id", type=int)
        date_s = request.form.get("appointment_date", "").strip()
        ap.time_slot = request.form.get("time_slot", "").strip()
        ap.status = request.form.get("status", "scheduled").strip()
        try:
            ap.appointment_date = datetime.strptime(date_s, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date.", "danger")
            return render_template(
                "admin/appointment_form.html",
                appointment=ap,
                doctors=doctors,
                patients=patients,
                all_slots=all_time_slots(),
                slot_label=slot_label,
            )
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not save — possible slot conflict.", "danger")
            return render_template(
                "admin/appointment_form.html",
                appointment=ap,
                doctors=doctors,
                patients=patients,
                all_slots=all_time_slots(),
                slot_label=slot_label,
            )
        flash("Appointment updated.", "success")
        return redirect(url_for("admin.appointments_list"))
    return render_template(
        "admin/appointment_form.html",
        appointment=ap,
        doctors=doctors,
        patients=patients,
        all_slots=all_time_slots(),
        slot_label=slot_label,
    )


@admin_bp.route("/appointments/<int:aid>/delete", methods=["POST"])
@admin_required
def appointments_delete(aid):
    ap = Appointment.query.get_or_404(aid)
    db.session.delete(ap)
    db.session.commit()
    flash("Appointment deleted.", "info")
    return redirect(url_for("admin.appointments_list"))


@admin_bp.route("/appointments/add", methods=["GET", "POST"])
@admin_required
def add_appointment():
    """Admin can add a new appointment for a patient with a doctor."""
    doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
    patients = Patient.query.order_by(Patient.name).all()
    
    if request.method == "POST":
        patient_id = request.form.get("patient_id", type=int)
        doctor_id = request.form.get("doctor_id", type=int)
        date_s = request.form.get("appointment_date", "").strip()
        time_slot = request.form.get("time_slot", "").strip()

        if not patient_id or not doctor_id or not date_s or not time_slot:
            flash("All fields are required.", "danger")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        try:
            adate = datetime.strptime(date_s, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "danger")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        if adate < date.today():
            flash("Cannot book appointments in the past.", "danger")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        # Check doctor's unavailability
        selected_doctor = Doctor.query.get(doctor_id)
        if selected_doctor and selected_doctor.unavailability_start_date and selected_doctor.unavailability_end_date:
            if selected_doctor.unavailability_start_date <= adate <= selected_doctor.unavailability_end_date:
                flash(f"{selected_doctor.name} is unavailable on {adate.strftime('%Y-%m-%d')}.", "danger")
                return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        if time_slot not in all_time_slots():
            flash("Invalid time slot.", "danger")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        # Double-booking check
        taken = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=adate,
            time_slot=time_slot,
        ).first()
        if taken:
            flash("That slot is already taken. Please choose another time.", "warning")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

        new_appt = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=adate,
            time_slot=time_slot,
            status="scheduled",
        )
        db.session.add(new_appt)
        try:
            db.session.commit()
            flash("Appointment added successfully.", "success")
            return redirect(url_for("admin.appointments_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding appointment: {e}", "danger")
            return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)

    return render_template("admin/appointment_form.html", doctors=doctors, patients=patients, all_slots=all_time_slots(), slot_label=slot_label)


# --- Departments (view + add for completeness) ---


@admin_bp.route("/departments", methods=["GET", "POST"])
@admin_required
def departments():
    """List departments with a Bar Chart of doctors per department."""
    from sqlalchemy import func
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        desc = request.form.get("description", "").strip()
        if name and not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=desc))
            db.session.commit()
            flash("Department added.", "success")
        else:
            flash("Invalid or duplicate department name.", "danger")
        return redirect(url_for("admin.departments"))
        
    rows = Department.query.order_by(Department.name).all()
    
    # Chart Data: Doctors per department
    dept_counts = db.session.query(Department.name, func.count(Doctor.id))\
        .outerjoin(Doctor, Doctor.department_id == Department.id)\
        .group_by(Department.id, Department.name)\
        .order_by(Department.name).all()
        
    chart_labels = [d[0] for d in dept_counts]
    chart_values = [d[1] for d in dept_counts]
    
    return render_template("admin/departments.html", departments=rows, chart_labels=chart_labels, chart_values=chart_values)




@admin_bp.route("/reports")
@admin_required
def reports():
    """Simple analytics for demo."""
    from sqlalchemy import func

    # Count doctors per department (outer join so empty departments still appear)
    by_dept = (
        db.session.query(Department.name, func.count(Doctor.id))
        .outerjoin(Doctor, Doctor.department_id == Department.id)
        .group_by(Department.id, Department.name)
        .order_by(Department.name)
        .all()
    )
    appt_by_status = (
        db.session.query(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status).all()
    )
    return render_template("admin/reports.html", by_dept=by_dept, appt_by_status=appt_by_status)


# --- Billing Desk ---

@admin_bp.route("/billing")
@admin_required
def billing_desk():
    """Manage invoices and payments."""
    appts = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template("admin/billing.html", appointments=appts)


@admin_bp.route("/appointment/<int:appt_id>/invoice", methods=["POST"])
@admin_required
def generate_invoice(appt_id):
    """Set invoice amount for an appointment."""
    ap = Appointment.query.get_or_404(appt_id)
    amount = request.form.get("amount", type=float)
    if amount and amount > 0:
        ap.invoice_amount = amount
        db.session.commit()
        flash(f"Invoice generated for ${amount}.", "success")
    return redirect(url_for("admin.billing_desk"))


@admin_bp.route("/appointment/<int:appt_id>/mark-paid", methods=["POST"])
@admin_required
def mark_paid(appt_id):
    """Mark an invoice as paid."""
    ap = Appointment.query.get_or_404(appt_id)
    ap.is_paid = True
    db.session.commit()
    flash("Invoice marked as paid.", "success")
    return redirect(url_for("admin.billing_desk"))


# --- Ward Management ---

@admin_bp.route("/wards")
@admin_required
def ward_management():
    """Track rooms and beds."""
    wards = Ward.query.order_by(Ward.room_number, Ward.bed_number).all()
    patients = Patient.query.order_by(Patient.name).all()
    
    stats = {
        "total_beds": Ward.query.count(),
        "occupied_beds": Ward.query.filter_by(is_available=False).count(),
        "available_beds": Ward.query.filter_by(is_available=True).count(),
        "icu_beds": Ward.query.filter_by(ward_type="ICU").count()
    }
    
    return render_template(
        "admin/ward.html", 
        wards=wards, 
        patients=patients,
        **stats
    )


@admin_bp.route("/wards/add", methods=["POST"])
@admin_required
def add_bed():
    """Add a new bed to a room."""
    room = request.form.get("room", "").strip()
    bed = request.form.get("bed", "").strip()
    wtype = request.form.get("type", "General").strip()
    
    if room and bed:
        new_ward = Ward(room_number=room, bed_number=bed, ward_type=wtype)
        db.session.add(new_ward)
        db.session.commit()
        flash(f"Bed {bed} in Room {room} added.", "success")
    return redirect(url_for("admin.ward_management"))


@admin_bp.route("/wards/<int:ward_id>/assign", methods=["POST"])
@admin_required
def assign_bed(ward_id):
    """Assign a patient to a bed."""
    w = Ward.query.get_or_404(ward_id)
    pid = request.form.get("patient_id", type=int)
    if pid:
        w.patient_id = pid
        w.is_available = False
        db.session.commit()
        flash("Patient assigned to bed.", "success")
    return redirect(url_for("admin.ward_management"))


@admin_bp.route("/wards/<int:ward_id>/release", methods=["POST"])
@admin_required
def release_bed(ward_id):
    """Release a bed."""
    w = Ward.query.get_or_404(ward_id)
    w.patient_id = None
    w.is_available = True
    db.session.commit()
    flash("Bed released.", "info")
    return redirect(url_for("admin.ward_management"))


# --- Lab Management ---

@admin_bp.route("/lab-requests", methods=["GET", "POST"])
@admin_required
def lab_desk():
    """Admin desk for processing pending lab requests."""
    if request.method == "POST":
        appt_id = request.form.get("appt_id", type=int)
        lab_link = request.form.get("lab_result_link", "").strip()
        
        if appt_id and lab_link:
            ap = Appointment.query.get_or_404(appt_id)
            ap.lab_result_link = lab_link
            # Once uploaded, we can mark results as completed or results_ready depending on system. 
            # We'll set status to requested format: updating link visible to doctor and patient.
            # We can advance status to results_ready so doctor knows.
            if ap.status == "pending_lab":
                ap.status = "completed" # Assuming end of consultation or just kept as 'results_ready'
            db.session.commit()
            flash("Lab results successfully linked.", "success")
        return redirect(url_for("admin.lab_desk"))
    
    pending_requests = Appointment.query.filter_by(status="pending_lab").order_by(Appointment.appointment_date).all()
    # Also show recently completed for visibility
    completed_requests = Appointment.query.filter(Appointment.lab_result_link != "").order_by(Appointment.appointment_date.desc()).limit(10).all()
    
    return render_template("admin/lab_desk.html", pending=pending_requests, completed=completed_requests)
