import datetime

from models import Appointment, SessionLocker


db = SessionLocker()

appointment = Appointment(
    patient_name="Rahul Kumar",
    doctor_name="Dr. Sharma",
    appointment_date=datetime.datetime(2026, 9, 20, 10, 30),
    reason="Fever",
    status="scheduled"
)

db.add(appointment)
db.commit()

print("Data inserted successfully!")

db.close()