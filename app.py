from flask import Flask, render_template, request, redirect, url_for, flash
import database as db
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    # Fetch summary stats
    patients_count = len(db.fetch_all("SELECT PatientID FROM Patients"))
    doctors_count = len(db.fetch_all("SELECT DoctorID FROM Doctors"))
    appointments_count = len(db.fetch_all("SELECT AppointmentID FROM Appointments"))
    
    return render_template('index.html', p_count=patients_count, d_count=doctors_count, a_count=appointments_count)

# --- Patients Management ---
@app.route('/patients', methods=['GET', 'POST'])
def manage_patients():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form['address']
        
        query = "INSERT INTO Patients (FirstName, LastName, DOB, Gender, ContactNumber, Address) VALUES (%s, %s, %s, %s, %s, %s)"
        if db.execute_query(query, (fname, lname, dob, gender, contact, address)):
            flash('Patient added successfully!', 'success')
        else:
            flash('Failed to add patient.', 'error')
        return redirect(url_for('manage_patients'))
        
    patients = db.fetch_all("SELECT * FROM Patients ORDER BY CreatedAt DESC")
    return render_template('patient.html', patients=patients)

# --- Doctors Management ---
@app.route('/doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        spec = request.form['specialization']
        contact = request.form['contact']
        email = request.form['email']
        
        query = "INSERT INTO Doctors (FirstName, LastName, Specialization, ContactNumber, Email) VALUES (%s, %s, %s, %s, %s)"
        if db.execute_query(query, (fname, lname, spec, contact, email)):
            flash('Doctor added successfully!', 'success')
        else:
            flash('Failed to add doctor. Email might be duplicate.', 'error')
        return redirect(url_for('manage_doctors'))
        
    doctors = db.fetch_all("SELECT * FROM Doctors ORDER BY LastName")
    return render_template('doctor.html', doctors=doctors)

# --- Appointments Booking & Management ---
@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if request.method == 'POST':
        if 'book' in request.form:
            p_id = request.form['patient_id']
            d_id = request.form['doctor_id']
            date = request.form['date']
            time = request.form['time']
            
            # Using our Stored Procedure with ACIDs
            message = db.call_book_appointment_proc(p_id, d_id, date, time)
            if 'Error' in message:
                flash(message, 'error')
            else:
                flash(message, 'success')
                
        elif 'update_status' in request.form:
            a_id = request.form['appointment_id']
            new_status = request.form['status']
            # This triggers AfterAppointmentComplete if set to 'Completed'
            query = "UPDATE Appointments SET Status = %s WHERE AppointmentID = %s"
            if db.execute_query(query, (new_status, a_id)):
                flash(f'Appointment marked as {new_status}.', 'success')
                
        return redirect(url_for('manage_appointments'))
        
    appointments = db.fetch_all('''
        SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, a.Status,
               p.FirstName as PName, p.LastName as PLName,
               d.FirstName as DName, d.LastName as DLName
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC
    ''')
    patients = db.fetch_all("SELECT PatientID, FirstName, LastName FROM Patients")
    doctors = db.fetch_all("SELECT DoctorID, FirstName, LastName, Specialization FROM Doctors")
    
    return render_template('appointment.html', appointments=appointments, patients=patients, doctors=doctors)

# --- Billing Management ---
@app.route('/billing', methods=['GET', 'POST'])
def manage_billing():
    if request.method == 'POST':
        # Process Payment
        bill_id = request.form['bill_id']
        query = "UPDATE Billing SET PaymentStatus = 'Paid' WHERE BillID = %s"
        if db.execute_query(query, (bill_id,)):
            flash('Bill marked as paid.', 'success')
        return redirect(url_for('manage_billing'))
        
    bills = db.fetch_all('''
        SELECT b.BillID, b.Amount, b.DateIssued, b.PaymentStatus,
               p.FirstName, p.LastName
        FROM Billing b
        JOIN Patients p ON b.PatientID = p.PatientID
        ORDER BY b.DateIssued DESC
    ''')
    return render_template('billing.html', bills=bills)

# --- Medical History ---
@app.route('/history', methods=['GET', 'POST'])
def view_history():
    if request.method == 'POST':
        p_id = request.form['patient_id']
        d_id = request.form['doctor_id']
        diag = request.form['diagnosis']
        treat = request.form['treatment']
        query = "INSERT INTO MedicalHistory (PatientID, DoctorID, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)"
        if db.execute_query(query, (p_id, d_id, diag, treat)):
            flash('Medical record added successfully.', 'success')
        else:
            flash('Failed to add record.', 'error')
        return redirect(url_for('view_history'))

    history_records = db.fetch_all('''
        SELECT m.RecordID, m.DateRecorded, m.Diagnosis, m.Treatment,
               p.FirstName as PFName, p.LastName as PLName,
               d.FirstName as DFName, d.LastName as DLName
        FROM MedicalHistory m
        JOIN Patients p ON m.PatientID = p.PatientID
        JOIN Doctors d ON m.DoctorID = d.DoctorID
        ORDER BY m.DateRecorded DESC
    ''')
    patients = db.fetch_all("SELECT PatientID, FirstName, LastName FROM Patients")
    doctors = db.fetch_all("SELECT DoctorID, FirstName, LastName, Specialization FROM Doctors")
    return render_template('history.html', records=history_records, patients=patients, doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
