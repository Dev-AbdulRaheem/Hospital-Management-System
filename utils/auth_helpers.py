"""Session-based auth decorators for patient, doctor, and admin areas."""
from functools import wraps

from flask import flash, redirect, request, session, url_for


def patient_required(f):
    """Require logged-in patient (session['patient_id'])."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("patient_id"):
            flash("Please sign in as a patient to continue.", "warning")
            # Pass next URL and doctor_id if booking
            next_url = request.endpoint
            doctor_id = request.args.get("doctor_id")
            return redirect(url_for("patient.login", next=next_url, doctor_id=doctor_id))
        return f(*args, **kwargs)

    return wrapped


def doctor_required(f):
    """Require logged-in doctor (session['doctor_id'])."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("doctor_id"):
            flash("Please sign in as a doctor to continue.", "warning")
            return redirect(url_for("doctor.login"))
        return f(*args, **kwargs)

    return wrapped


def admin_required(f):
    """Require logged-in admin (session['admin_id'])."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please sign in as an administrator.", "warning")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return wrapped
