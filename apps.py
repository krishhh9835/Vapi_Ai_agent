from fastapi import FastAPI, HTTPException, Depends
import datetime as dt
from typing import List, Optional
from models import Appointment, init_db, get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

# Initialize database tables on startup
init_db()

app = FastAPI(title="AIIMS Delhi Appointment Tool System")

# ==========================================
#          PYDANTIC SCHEMAS (VAPI)
# ==========================================

class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str
    appointment_date: dt.datetime

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    doctor_name: str
    created_at: dt.datetime
    appointment_date: dt.datetime
    reason: str
    canceled: bool
    vapi_message: str  # Direct text response for the AI agent to read out loud

class CancelAppointmentRequest(BaseModel):
    appointment_id: int
    patient_name: str

class CancelAppointmentResponse(BaseModel):
    status: str
    vapi_message: str

class CheckAppointmentRequest(BaseModel):
    appointment_id: int
    patient_name: str
    target_date: dt.date

class CheckAppointmentResponse(BaseModel):
    status: str
    vapi_message: str

class CheckAvailabilityRequest(BaseModel):
    requested_datetime: dt.datetime

class CheckAvailabilityResponse(BaseModel):
    available: bool
    vapi_message: str


# ==========================================
#               API ENDPOINTS
# ==========================================

@app.post("/scheduleappointment/", response_model=AppointmentResponse)
def schedule_function(request: AppointmentRequest, db: Session = Depends(get_db)):
    """
    Creates a new appointment and returns a confirmation string containing the new ID.
    """
    new_appointment = Appointment(
        patient_name=request.patient_name,
        reason=request.reason,
        appointment_date=request.appointment_date,
        doctor_name="TBD",
        canceled=False
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    readable_date = new_appointment.appointment_date.strftime('%B %d at %I:%M %p')
    vapi_msg = f"Your appointment has been successfully booked for {readable_date}. Your unique Appointment ID is {new_appointment.id}. Please save this ID to check or cancel your booking later."

    return AppointmentResponse(
        id=new_appointment.id,
        patient_name=new_appointment.patient_name,
        doctor_name=getattr(new_appointment, 'doctor_name', 'TBD'),
        appointment_date=new_appointment.appointment_date,
        reason=new_appointment.reason,
        created_at=new_appointment.created_at,
        canceled=new_appointment.canceled,
        vapi_message=vapi_msg
    )


@app.post("/cancelappointment/", response_model=CancelAppointmentResponse)
def cancel_function(request: CancelAppointmentRequest, db: Session = Depends(get_db)):
    """
    Verifies the user via ID and patient name, then sets canceled to True.
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == request.appointment_id,
        Appointment.patient_name.ilike(request.patient_name)  # Case-insensitive check
    ).first()

    if not appointment:
        return CancelAppointmentResponse(
            status="error",
            vapi_message="I'm sorry, I could not find an active appointment with that ID and patient name. Please double check the details."
        )

    if appointment.canceled:
        return CancelAppointmentResponse(
            status="info",
            vapi_message="Our records show that this appointment has already been canceled."
        )

    appointment.canceled = True
    db.commit()

    return CancelAppointmentResponse(
        status="success",
        vapi_message=f"Thank you. Your appointment with ID {appointment.id} for {appointment.patient_name} has been successfully canceled."
    )


@app.post("/checkappointment/", response_model=CheckAppointmentResponse)
def check_function(request: CheckAppointmentRequest, db: Session = Depends(get_db)):
    """
    Checks if a specific patient ID is scheduled to come in on a targeted date.
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == request.appointment_id,
        Appointment.patient_name.ilike(request.patient_name)
    ).first()

    if not appointment:
        return CheckAppointmentResponse(
            status="error",
            vapi_message="I was unable to locate any booking records matching that ID and name."
        )

    if appointment.canceled:
        return CheckAppointmentResponse(
            status="info",
            vapi_message="Your booking for this appointment ID was previously canceled."
        )

    if appointment.appointment_date.date() == request.target_date:
        readable_time = appointment.appointment_date.strftime('%I:%M %p')
        return CheckAppointmentResponse(
            status="match",
            vapi_message=f"Yes, you have an active booking confirmed for that date at {readable_time}."
        )
    else:
        actual_date = appointment.appointment_date.strftime('%B %d')
        return CheckAppointmentResponse(
            status="mismatch",
            vapi_message=f"No, your appointment ID is actually scheduled for {actual_date}, not the date you requested."
        )


@app.post("/checkavailability/", response_model=CheckAvailabilityResponse)
def check_availability_function(request: CheckAvailabilityRequest, db: Session = Depends(get_db)):
    """
    Checks if an existing active appointment overlaps within a 30-minute block of the requested time.
    """
    # 30-minute reservation safety window block configuration
    start_window = request.requested_datetime - dt.timedelta(minutes=29)
    end_window = request.requested_datetime + dt.timedelta(minutes=29)

    overlapping_appointment = db.query(Appointment).filter(
        Appointment.appointment_date >= start_window,
        Appointment.appointment_date <= end_window,
        Appointment.canceled == False
    ).first()

    if overlapping_appointment:
        suggested_time = request.requested_datetime.strftime('%I:%M %p')
        return CheckAvailabilityResponse(
            available=False,
            vapi_message=f"I am sorry, but {suggested_time} is already booked by another patient. Would you like to check a different time slot?"
        )
    
    formatted_time = request.requested_datetime.strftime('%A, %B %d at %I:%M %p')
    return CheckAvailabilityResponse(
        available=True,
        vapi_message=f"Yes! {formatted_time} is completely free. We can proceed with scheduling your booking for this slot."
    )


if __name__ == "__main__":
    uvicorn.run("apps:app", host="127.0.0.1", port=8000, reload=True)
