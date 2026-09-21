import streamlit as st
import requests
import datetime as dt
import pandas as pd

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Agent Appointment Manager", page_icon="📅", layout="wide")
st.title("📅 AI Agent Appointment Dashboard")

tab1, tab2, tab3 = st.tabs(["🔍 View & Filter Appointments", "➕ Schedule Appointment", "❌ Cancel Appointment"])

with tab1:
    st.header("Appointment Logs")
    
    col1, col2 = st.columns(2)
    with col1:
        date_a = st.date_input("Filter Date A", value=None)
    with col2:
        date_b = st.date_input("Filter Date B (Optional for alternate range)", value=None)
        
    payload = {}
    if date_a:
        payload["date_a"] = date_a.isoformat()
    if date_b:
        payload["date_b"] = date_b.isoformat()
        
    try:
        response = requests.post(f"{FASTAPI_URL}/listappointment/", json=payload)
        if response.status_code == 200:
            appointments = response.json()
            if appointments:
                df = pd.DataFrame(appointments)
                df = df[["id", "patient_name", "doctor_name", "appointment_date", "reason", "canceled", "created_at"]]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No appointments found for the selected dates.")
        else:
            st.error(f"Backend returned an error status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.warning("Could not connect to FastAPI backend. Make sure your server is running on port 8000.")

with tab2:
    st.header("Book a New Slot")
    with st.form("schedule_form", clear_on_submit=True):
        patient_name = st.text_input("Patient Name")
        reason = st.text_area("Reason for Visit")
        app_date = st.date_input("Appointment Date", value=dt.date.today())
        app_time = st.time_input("Appointment Time", value=dt.time(10, 0))
        
        submitted = st.form_submit_button("Schedule Appointment")
        if submitted:
            if patient_name and reason:
                combined_datetime = dt.datetime.combine(app_date, app_time)
                sched_payload = {
                    "patient_name": patient_name,
                    "reason": reason,
                    "appointment_date": combined_datetime.isoformat()
                }
                res = requests.post(f"{FASTAPI_URL}/scheduleappointment/", json=sched_payload)
                if res.status_code == 200:
                    st.success(f"Successfully scheduled appointment for {patient_name}!")
                    st.rerun()
                else:
                    st.error("Failed to schedule appointment.")
            else:
                st.warning("Please fill in all the required fields.")

with tab3:
    st.header("Cancel an Existing Slot")
    with st.form("cancel_form", clear_on_submit=True):
        cancel_name = st.text_input("Patient Name")
        cancel_date = st.date_input("Appointment Date", value=dt.date.today())
        
        submitted_cancel = st.form_submit_button("Cancel Appointment")
        if submitted_cancel:
            if cancel_name:
                cancel_payload = {
                    "patient_name": cancel_name,
                    "appointment_date": cancel_date.isoformat()
                }
                res = requests.post(f"{FASTAPI_URL}/cancelappointment/", json=cancel_payload)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Done! {data['message']} Total records changed: {data['canceled_count']}")
                    st.rerun()
                elif res.status_code == 404:
                    st.error("No matching active appointment found for that layout.")
                else:
                    st.error("Failed to process cancellation request.")
            else:
                st.warning("Please specify a patient name.")
