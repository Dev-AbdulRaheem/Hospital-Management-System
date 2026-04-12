"""Seed database with departments, doctors, patients, sample appointments."""
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from models import db, Admin, Department, Doctor, Patient, Appointment, Ward


# 18 departments with short descriptions for landing / services section
DEPARTMENTS_DATA = [
    ("Cardiology", "Heart and cardiovascular system — diagnostics, intervention, and rehabilitation."),
    ("Neurology", "Brain, spinal cord, and nervous system disorders."),
    ("Orthopedics", "Bones, joints, muscles, and sports injuries."),
    ("Pediatrics", "Medical care for infants, children, and adolescents."),
    ("Oncology", "Cancer diagnosis, chemotherapy, and supportive care."),
    ("Dermatology", "Skin, hair, and nail conditions."),
    ("Ophthalmology", "Eye health, vision correction, and surgery."),
    ("ENT", "Ear, nose, and throat conditions and surgery."),
    ("Gastroenterology", "Digestive system and liver disorders."),
    ("Pulmonology", "Lungs and respiratory diseases."),
    ("Nephrology", "Kidney diseases and dialysis coordination."),
    ("Urology", "Urinary tract and male reproductive health."),
    ("Endocrinology", "Hormones, diabetes, and metabolic disorders."),
    ("Rheumatology", "Autoimmune and musculoskeletal inflammatory diseases."),
    ("Psychiatry", "Mental health assessment and treatment."),
    ("Obstetrics & Gynecology", "Women's health, pregnancy, and childbirth."),
    ("Emergency Medicine", "24/7 acute care and trauma stabilization."),
    ("Radiology", "Imaging: X-ray, CT, MRI, and ultrasound."),
]


def seed_if_empty(app):
    """Populate demo data when tables are empty."""
    with app.app_context():
        if Department.query.first():
            return

        # Departments
        dept_objs = []
        for name, desc in DEPARTMENTS_DATA:
            d = Department(name=name, description=desc)
            db.session.add(d)
            dept_objs.append(d)
        db.session.flush()

        dept_by_name = {d.name: d.id for d in dept_objs}

        # 20 doctors — (name, email, department name, years, bio, fee, qualifications, unavailability_start, unavailability_end)
        doctors_spec = [
            ("Dr. Sarah Mitchell", "sarah.mitchell@hospital.demo", "Cardiology", 14, "Interventional cardiologist; focus on coronary disease.", 1500, "MD, FACC", None, None),
            ("Dr. James Chen", "james.chen@hospital.demo", "Neurology", 18, "Stroke and epilepsy specialist.", 1800, "MD, PhD", None, None),
            ("Dr. Priya Sharma", "priya.sharma@hospital.demo", "Orthopedics", 12, "Joint replacement and sports medicine.", 1200, "MD, FACS", date.today() + timedelta(days=10), date.today() + timedelta(days=15)),
            ("Dr. Emily Roberts", "emily.roberts@hospital.demo", "Pediatrics", 9, "General pediatrics and developmental care.", 800, "MD, FAAP", None, None),
            ("Dr. Michael Torres", "michael.torres@hospital.demo", "Oncology", 16, "Medical oncology and immunotherapy.", 2000, "MD, FACP", None, None),
            ("Dr. Lisa Park", "lisa.park@hospital.demo", "Dermatology", 11, "Cosmetic and medical dermatology.", 1000, "MD, FAAD", None, None),
            ("Dr. David Okonkwo", "david.okonkwo@hospital.demo", "Ophthalmology", 20, "Cataract and retinal surgery.", 1600, "MD, FACS", date.today() + timedelta(days=20), date.today() + timedelta(days=25)),
            ("Dr. Anna Weber", "anna.weber@hospital.demo", "ENT", 13, "Sinus and hearing disorders.", 900, "MD, FACS", None, None),
            ("Dr. Raj Patel", "raj.patel@hospital.demo", "Gastroenterology", 15, "IBD and liver disease.", 1300, "MD, AGAF", None, None),
            ("Dr. Helen Foster", "helen.foster@hospital.demo", "Pulmonology", 10, "Asthma, COPD, and sleep apnea.", 1100, "MD, FCCP", None, None),
            ("Dr. Omar Hassan", "omar.hassan@hospital.demo", "Nephrology", 17, "Chronic kidney disease management.", 1400, "MD, FASN", None, None),
            ("Dr. Kevin Liu", "kevin.liu@hospital.demo", "Urology", 12, "Minimally invasive urologic surgery.", 1200, "MD, FACS", None, None),
            ("Dr. Maria Gonzalez", "maria.gonzalez@hospital.demo", "Obstetrics & Gynecology", 16, "High-risk pregnancy and minimally invasive gynecology.", 1700, "MD, FACOG", None, None),
            ("Dr. Thomas Blake", "thomas.blake@hospital.demo", "Rheumatology", 14, "Lupus and arthritis care.", 1300, "MD, FACR", None, None),
            ("Dr. Sophie Martin", "sophie.martin@hospital.demo", "Psychiatry", 11, "Adult psychiatry and CBT.", 1500, "MD, ABPN", None, None),
            ("Dr. Andrew Wright", "andrew.wright@hospital.demo", "Emergency Medicine", 9, "Trauma and acute care.", 1000, "MD, FACEP", None, None),
            ("Dr. Fatima Al-Rashid", "fatima.alrashid@hospital.demo", "Radiology", 13, "Diagnostic imaging and neuroradiology.", 1200, "MD, DABR", None, None),
            ("Dr. Victor Nwosu", "victor.nwosu@hospital.demo", "Cardiology", 7, "Heart failure and imaging.", 1400, "MD", None, None),
            ("Dr. Nina Kowalski", "nina.kowalski@hospital.demo", "Neurology", 6, "Movement disorders and MS.", 1300, "MD", None, None),
            ("Dr. Mei Zhang", "mei.zhang@hospital.demo", "Endocrinology", 8, "Diabetes and thyroid disorders.", 1100, "MD", None, None),
        ]

        pwd = generate_password_hash("doctor123")
        # Unsplash professional medical photo IDs for variety
       # Single professional image for all males and all females
        MALE_DOC_IMG = "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?q=80&w=400&auto=format&fit=crop"
        FEMALE_DOC_IMG = "https://images.unsplash.com/photo-1594824476967-48c8b964273f?q=80&w=400&auto=format&fit=crop"

        for name, email, dname, years, bio, fee, qualifications, unavail_start, unavail_end in doctors_spec:
            did = dept_by_name[dname]
            
            # Identify gender by name to assign the correct image
            if any(n in name for n in ["Sarah", "Priya", "Emily", "Lisa", "Anna", "Helen", "Maria", "Sophie", "Fatima", "Nina", "Mei"]):
                img_url = FEMALE_DOC_IMG
            else:
                img_url = MALE_DOC_IMG

            doc = Doctor(
                name=name,
                email=email,
                password_hash=pwd,
                phone="+1-555-0100",
                experience_years=years,
                bio=bio,
                department_id=did,
                consultation_fee=fee,
                is_active=True,
                unavailability_start_date=unavail_start,
                unavailability_end_date=unavail_end,
                qualifications=qualifications,
                image_url=img_url
            )
            db.session.add(doc)
        # 12 patients (at least 10)
        patients_data = [
            ("Alice Johnson", "alice.j@email.com", "1990-04-12", "Female"),
            ("Bob Smith", "bob.smith@email.com", "1985-08-22", "Male"),
            ("Carol White", "carol.w@email.com", "1992-11-03", "Female"),
            ("Dan Brown", "dan.brown@email.com", "1978-01-30", "Male"),
            ("Eva Martinez", "eva.m@email.com", "2000-07-15", "Female"),
            ("Frank Lee", "frank.lee@email.com", "1988-12-01", "Male"),
            ("Grace Taylor", "grace.t@email.com", "1995-05-20", "Female"),
            ("Henry Davis", "henry.d@email.com", "1982-09-09", "Male"),
            ("Ivy Chen", "ivy.chen@email.com", "1998-02-28", "Female"),
            ("Jack Wilson", "jack.w@email.com", "1991-06-14", "Male"),
            ("Kate Moore", "kate.m@email.com", "1987-10-25", "Female"),
            ("Leo Anderson", "leo.a@email.com", "1993-03-07", "Male"),
        ]
        ppwd = generate_password_hash("patient123")
        for name, email, dob_s, gender in patients_data:
            y, m, d = map(int, dob_s.split("-"))
            p = Patient(
                name=name,
                email=email,
                password_hash=ppwd,
                phone="+1-555-0200",
                date_of_birth=date(y, m, d),
                gender=gender,
                address="Demo City",
            )
            db.session.add(p)

        admin = Admin(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            full_name="System Administrator",
        )
        db.session.add(admin)

        db.session.flush()

        docs = Doctor.query.order_by(Doctor.id).all()
        pats = Patient.query.order_by(Patient.id).all()
        if docs and pats:
            today = date.today()
            a1 = Appointment(
                patient_id=pats[0].id,
                doctor_id=docs[0].id,
                appointment_date=today - timedelta(days=5),
                time_slot="10:00",
                status="completed",
                diagnosis="Stable angina — medication adjusted.",
                notes="Follow-up in 3 months.",
            )
            a2 = Appointment(
                patient_id=pats[1].id,
                doctor_id=docs[1].id,
                appointment_date=today + timedelta(days=3),
                time_slot="11:00",
                status="scheduled",
                notes="",
            )
            a3 = Appointment(
                patient_id=pats[2].id,
                doctor_id=docs[0].id,
                appointment_date=today + timedelta(days=7),
                time_slot="14:30",
                status="scheduled",
                notes="",
            )
            db.session.add_all([a1, a2, a3])

        # Wards
        wards_data = [
            ("101", "A", "General"), ("101", "B", "General"),
            ("102", "A", "General"), ("102", "B", "General"),
            ("201", "1", "ICU"), ("201", "2", "ICU"),
            ("301", "P", "Special"), ("301", "Q", "Special")
        ]
        for room, bed, wtype in wards_data:
            w = Ward(room_number=room, bed_number=bed, ward_type=wtype)
            db.session.add(w)

        db.session.commit()
