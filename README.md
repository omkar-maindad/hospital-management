# Hospital Patient Management System

This mini-project is built for the **SPPU SE AIDS DBMS Laboratory**. It implements a complete end-to-end relational database application using purely standard SQL, PL/SQL elements, Python (Flask), and a modern Web UI.

## Features implemented mapped to Syllabus
1. **ER Model & Relational Tables (Unit I, III):** Normalized tables (`db_schema.sql`) for Patients, Doctors, Appointments, Billing in BCNF.
2. **Smart Data Querying & PL/SQL (Unit II):** 
   - Uses parameterized SQL in Python.
   - Contains a **Stored Procedure** (`BookAppointment`) for robust logic checking.
   - Contains a **Database Trigger** (`AfterAppointmentComplete`) that automatically calculates and inserts a pending bill.
3. **Transaction Management (Unit IV):** 
   - `START TRANSACTION`, `COMMIT`, and `ROLLBACK` logic handles concurrency and consistency inside the `BookAppointment` procedure.
4. **NoSQL (Unit V):** Not used intentionally; opted to keep the architecture perfectly robust and reliable on standard relational principles as verified.

## How to Setup & Run locally

### Step 1: Initialize Database
1. Open **MySQL Workbench**.
2. Create a new query tab and open `db_schema.sql`.
3. Execute the entire file. This will create the `hospital_db` database, tables, triggers, and some sample initial data.

### Step 2: Configure Environment
1. In the project folder, open the `.env.example` file.
2. Update `DB_PASSWORD` with your actual MySQL Workbench root password (if you have one).
3. Right-click `.env.example` and rename it to exactly `.env`.

### Step 3: Run the Python App
Open PowerShell or Command Prompt in this directory and execute:
```powershell
# Create a virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (wait for this to finish)
pip install -r requirements.txt

# Run the Flask Application
python app.py
```

### Step 4: Open the Website
Once running, go to your browser and open `http://127.0.0.1:5000` to view the modern, dynamic UI.
