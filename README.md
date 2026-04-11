# Hospital Management System (HMS)

A Flask-based web application for academic demonstration: public hospital site, patient appointments, doctor clinical notes, and admin CRUD.

## Folder structure

```
test4/
├── app.py                 # Application factory & entry point
├── config.py              # Configuration (SQLite path, secret key)
├── requirements.txt
├── README.md
├── instance/
│   └── hms.db             # SQLite database (created on first run)
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   ├── department.py
│   ├── doctor.py
│   ├── patient.py
│   ├── appointment.py
│   └── admin.py
├── routes/                # Blueprints
│   ├── public.py          # Landing, doctors, about, contact, APIs
│   ├── patient.py         # Patient auth & booking
│   ├── doctor.py          # Doctor dashboard & notes
│   └── admin.py           # Admin CRUD & reports
├── utils/
│   ├── seed.py            # Demo data (18 departments, 20 doctors, 12 patients)
│   ├── appointment_slots.py
│   └── auth_helpers.py
├── static/
│   ├── css/style.css
│   └── js/                # main.js, landing.js, booking.js, chatbot.js
└── templates/             # Jinja2 HTML (Bootstrap 5)
```

## Database schema (SQLite)

| Table | Purpose |
|-------|---------|
| **departments** | `id`, `name`, `description` |
| **doctors** | `id`, `name`, `email`, `password_hash`, `phone`, `experience_years`, `bio`, `department_id` (FK) |
| **patients** | `id`, `name`, `email`, `password_hash`, `phone`, `date_of_birth`, `gender`, `address` |
| **appointments** | `id`, `patient_id`, `doctor_id`, `appointment_date`, `time_slot`, `status`, `diagnosis`, `notes` |
| **admins** | `id`, `username`, `password_hash`, `full_name` |

**Constraint:** `UNIQUE(doctor_id, appointment_date, time_slot)` prevents double booking of the same slot.

## Demo accounts (after seed)

| Role | Identifier | Password |
|------|------------|----------|
| Admin | `admin` | `admin123` |
| Any seeded doctor | see Doctors page / DB (e.g. `sarah.mitchell@hospital.demo`) | `doctor123` |
| Any seeded patient | e.g. `alice.j@email.com` | `patient123` |

Delete `instance/hms.db` to recreate the database and re-run seed (empty departments table triggers seed).

## Run locally (Windows)

1. **Python 3.10+** recommended.

2. Open a terminal in the project folder:

   ```powershell
   cd c:\Users\FMS-PC-2025\Desktop\test4
   python -m pip install -r requirements.txt
   python app.py
   ```

3. Open a browser: **http://127.0.0.1:5000**

4. Optional (Flask CLI):

   ```powershell
   set FLASK_APP=app.py
   flask run
   ```

## Features summary

- **Public:** Hero banner, 18 departments (services modal with doctors), doctors directory with profiles, about/contact, login hub.
- **Patient:** Register/login, dashboard (details, upcoming/history), book appointment with **dynamic available slots** and unique slot constraint.
- **Doctor:** Schedule, patient list, visit records (diagnosis, notes, status).
- **Admin:** Patients/doctors/appointments CRUD, departments, simple reports.
- **UI:** Bootstrap 5, sidebar dashboards, responsive layout, flash messages, FAQ chatbot widget.

## Security note

This project uses demo secrets and plain session cookies. For production, use HTTPS, strong `SECRET_KEY`, and a production-grade database.
