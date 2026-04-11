"""Public pages: landing, services, doctors directory, about, contact."""
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from models import Department, Doctor

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    """Homepage with hero, services preview, and CTA."""
    departments = Department.query.order_by(Department.name).all()
    featured_doctors = Doctor.query.limit(8).all()
    preselect_dept = request.args.get("dept", type=int)
    return render_template(
        "landing.html",
        departments=departments,
        featured_doctors=featured_doctors,
        preselect_dept=preselect_dept,
    )


@public_bp.route("/doctors")
def doctors_page():
    """Full list of doctors for public directory with search/filter."""
    q = request.args.get("q", "").strip()
    dept_id = request.args.get("dept", type=int)
    
    query = Doctor.query.join(Department)
    
    if q:
        query = query.filter(
            (Doctor.name.ilike(f"%{q}%")) | 
            (Doctor.specialization.ilike(f"%{q}%")) |
            (Department.name.ilike(f"%{q}%"))
        )
    
    if dept_id:
        query = query.filter(Doctor.department_id == dept_id)
        
    doctors = query.order_by(Doctor.name).all()
    departments = Department.query.order_by(Department.name).all()
    
    return render_template(
        "doctors_public.html", 
        doctors=doctors, 
        departments=departments,
        search_query=q,
        selected_dept=dept_id
    )


@public_bp.route("/doctor/<int:doctor_id>")
def doctor_detail(doctor_id):
    """Full doctor profile detail page."""
    doc = Doctor.query.get_or_404(doctor_id)
    return render_template("doctor_detail.html", doctor=doc)


@public_bp.route("/department/<int:dept_id>")
def department_detail(dept_id):
    """Dedicated department detail page."""
    dept = Department.query.get_or_404(dept_id)
    doctors = Doctor.query.filter_by(department_id=dept_id).order_by(Doctor.name).all()
    return render_template("department_detail.html", department=dept, doctors=doctors)


@public_bp.route("/login-hub")
def login_hub():
    """Choose Patient / Doctor / Admin login (linked from navbar Login)."""
    next_url = request.args.get("next")
    doctor_id = request.args.get("doctor_id")
    
    patient_login_url = url_for("patient.login")
    if next_url:
        patient_login_url = url_for("patient.login", next=next_url)
        if doctor_id:
            patient_login_url = url_for("patient.login", next=next_url, doctor_id=doctor_id)

    return render_template("login_hub.html", patient_login_url=patient_login_url)


@public_bp.route("/about")
def about():
    """About the hospital."""
    return render_template("about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact form — demo: flash success only (no email backend)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please fill in all contact fields.", "danger")
        else:
            flash("Thank you — your message has been received. We will respond soon.", "success")
            return redirect(url_for("public.contact"))
    return render_template("contact.html")


@public_bp.route("/api/department/<int:dept_id>")
def api_department_detail(dept_id):
    """JSON: department description + doctors for services modal / SPA."""
    dept = Department.query.get_or_404(dept_id)
    doctors = Doctor.query.filter_by(department_id=dept_id).order_by(Doctor.name).all()
    return jsonify(
        {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description or "",
            "doctors": [
                {
                    "id": d.id,
                    "name": d.name,
                    "specialization": dept.name,
                    "experience_years": d.experience_years,
                    "bio": d.bio or "",
                }
                for d in doctors
            ],
        }
    )


@public_bp.route("/api/doctor/<int:doctor_id>")
def api_doctor_detail(doctor_id):
    """JSON: full doctor profile for modal."""
    doc = Doctor.query.get_or_404(doctor_id)
    dept = doc.department
    return jsonify(
        {
            "id": doc.id,
            "name": doc.name,
            "email": doc.email,
            "phone": doc.phone,
            "experience_years": doc.experience_years,
            "bio": doc.bio or "",
            "department": dept.name if dept else "",
            "department_id": doc.department_id,
        }
    )
