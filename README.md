# Vapi AI Hospital Booking & Scheduling Agent

An intelligent, production-ready AI voice agent designed to automate **hospital appointment scheduling, booking, and real-time availability checks**. This system integrates custom backend business logic with conversational AI to provide seamless patient booking experiences.

## 🛠️ Tech Stack & Architecture

* **Conversational Voice AI**: [Vapi](https://vapi.ai) handles human-like voice synthesis, speech-to-text, and conversational routing.
* **Backend API Framework**: [FastAPI](https://tiangolo.com) drives the high-performance webhook endpoints and core booking logic.
* **Database**: [SQLite](https://sqlite.org) manages doctor schedules, patient profiles, and appointment blocks locally.
* **Environment Toolchain**: [uv](https://github.com) ensures ultra-fast, predictable Python dependency and virtual environment management.

---

## 🚀 Key Features

* 📅 **Real-time Availability Checks**: The agent dynamically checks the local SQLite database to confirm open slots before offering times to patients.
* ✍️ **Automated Scheduling & Updates**: Seamless creation, rescheduling, and cancellation of patient visits triggered directly by voice interaction.
* ⚡ **FastAPI Webhooks**: Low-latency endpoints designed to ingest tool-calls and function-routing payloads from Vapi instantly.

---

## 📥 Getting Started

### 1. Prerequisites
Ensure you have the `uv` toolchain installed on your local machine:
```bash
# Install uv if you haven't already
pip install uv
```

### 2. Installation & Setup
Clone the repository and navigate to your project directory:

```bash
cd Vapi_Ai_agent
```

Sync the project environment and install dependencies listed in `pyproject.toml` using `uv`:
```bash
uv sync
```

### 3. Database Initialization
Ensure your local `appointment.db` file is provisioned with the required schemas for doctors, slots, and patient schedules before booting the server.

### 4. Running the Server
Activate your virtual environment and launch the FastAPI server via Uvicorn:

```bash
uv run uvicorn main:app --reload
```
*Note: Replace `main:app` with your primary app entrypoint filename if it differs.*

---

## 🔗 Vapi Integration Details

This backend acts as a **Custom Tool / Function Caller** for your Vapi assistant. When a patient requests a booking during the call:
1. **Vapi** triggers a POST request to your FastAPI deployment.
2. The **FastAPI endpoint** processes the intent, queries/updates `appointment.db`, and formats a structured JSON response.
3. **Vapi** reads the output back to the patient in real time to finalize the booking.

---

## 🔒 Security & Environment
Never commit active databases or credential configurations to version control. Ensure your local `.env` and `appointment.db` files remain explicitly ignored by checking your `.gitignore`.
