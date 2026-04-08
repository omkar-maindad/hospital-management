from flask import Flask, render_template, request, redirect, url_for, flash, session
import database as db
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Security Authentication System ---
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'logged_in' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        # Fast presentation credentials
        if user == 'omkar_maindad' and pwd == 'Omkar@2006':
            session['logged_in'] = True
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid Administrator credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('System session terminated securely.', 'success')
    return redirect(url_for('login'))


@app.route('/')
def index():
    # Fetch summary stats with optimized single-value COUNT queries
    try:
        patients_count = db.fetch_all("SELECT COUNT(*) as cnt FROM Patients")[0]['cnt']
        doctors_count = db.fetch_all("SELECT COUNT(*) as cnt FROM Doctors")[0]['cnt']
        appointments_count = db.fetch_all("SELECT COUNT(*) as cnt FROM Appointments")[0]['cnt']
    except Exception:
        patients_count = doctors_count = appointments_count = 0
        
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
        
        # Anti-Duplication Engine
        duplicate = db.fetch_all("SELECT 1 FROM Patients WHERE FirstName=%s AND LastName=%s AND ContactNumber=%s", (fname, lname, contact))
        if duplicate:
            flash('ERROR: Identical Patient Record already exists.', 'error')
            return redirect(url_for('manage_patients'))
            
        query = "INSERT INTO Patients (FirstName, LastName, DOB, Gender, ContactNumber, Address) VALUES (%s, %s, %s, %s, %s, %s)"
        if db.execute_query(query, (fname, lname, dob, gender, contact, address)):
            flash('Patient added successfully!', 'success')
        else:
            flash('Failed to add patient.', 'error')
        return redirect(url_for('manage_patients'))
        
    patients = db.fetch_all("SELECT * FROM Patients ORDER BY PatientID ASC")
    return render_template('patient.html', patients=patients)

@app.route('/patients/edit/<int:id>', methods=['POST'])
def edit_patient(id):
    fname = request.form['first_name']
    lname = request.form['last_name']
    dob = request.form['dob']
    gender = request.form['gender']
    contact = request.form['contact']
    address = request.form['address']
    
    query = "UPDATE Patients SET FirstName=%s, LastName=%s, DOB=%s, Gender=%s, ContactNumber=%s, Address=%s WHERE PatientID=%s"
    if db.execute_query(query, (fname, lname, dob, gender, contact, address, id)):
        flash('Patient record updated successfully!', 'success')
    else:
        flash('Failed to update patient record.', 'error')
    return redirect(url_for('manage_patients'))

@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):
    if db.execute_query("DELETE FROM Patients WHERE PatientID=%s", (id,)):
        flash('Patient permanently deleted.', 'success')
    else:
        flash('Failed to delete patient.', 'error')
    return redirect(url_for('manage_patients'))

# --- Doctors Management ---
@app.route('/doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        spec = request.form['specialization']
        contact = request.form['contact']
        email = request.form['email']
        
        # Anti-Duplication Engine
        duplicate = db.fetch_all("SELECT 1 FROM Doctors WHERE Email=%s OR ContactNumber=%s", (email, contact))
        if duplicate:
            flash('ERROR: Doctor with this Email or Contact already registered.', 'error')
            return redirect(url_for('manage_doctors'))
            
        query = "INSERT INTO Doctors (FirstName, LastName, Specialization, ContactNumber, Email) VALUES (%s, %s, %s, %s, %s)"
        if db.execute_query(query, (fname, lname, spec, contact, email)):
            flash('Doctor added successfully!', 'success')
        else:
            flash('Failed to add doctor. Email might be duplicate.', 'error')
        return redirect(url_for('manage_doctors'))
        
    doctors = db.fetch_all("SELECT * FROM Doctors ORDER BY LastName")
    return render_template('doctor.html', doctors=doctors)

@app.route('/doctors/edit/<int:id>', methods=['POST'])
def edit_doctor(id):
    fname = request.form['first_name']
    lname = request.form['last_name']
    spec = request.form['specialization']
    contact = request.form['contact']
    email = request.form['email']
    
    query = "UPDATE Doctors SET FirstName=%s, LastName=%s, Specialization=%s, ContactNumber=%s, Email=%s WHERE DoctorID=%s"
    if db.execute_query(query, (fname, lname, spec, contact, email, id)):
        flash('Doctor details updated successfully!', 'success')
    else:
        flash('Failed to update doctor details. Email might already be taken.', 'error')
    return redirect(url_for('manage_doctors'))

@app.route('/doctors/delete/<int:id>', methods=['POST'])
def delete_doctor(id):
    if db.execute_query("DELETE FROM Doctors WHERE DoctorID=%s", (id,)):
        flash('Doctor permanently removed.', 'success')
    else:
        flash('Failed to remove doctor.', 'error')
    return redirect(url_for('manage_doctors'))

@app.route('/doctors/leave/<int:id>', methods=['POST'])
def mark_doctor_leave(id):
    leave_date = request.form['leave_date']
    exists = db.fetch_all("SELECT 1 FROM DoctorLeaves WHERE DoctorID=%s AND LeaveDate=%s", (id, leave_date))
    if exists:
        flash('Doctor is already marked on leave for this date.', 'error')
        return redirect(url_for('manage_doctors'))
    
    query = "INSERT INTO DoctorLeaves (DoctorID, LeaveDate) VALUES (%s, %s)"
    if db.execute_query(query, (id, leave_date)):
        flash('Leave scheduled successfully on the calendar.', 'success')
    else:
        flash('Failed to schedule leave.', 'error')
    return redirect(url_for('manage_doctors'))

# --- Appointments Booking & Management ---
@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if request.method == 'POST':
        if 'book' in request.form:
            p_id = request.form['patient_id']
            d_id = request.form['doctor_id']
            date = request.form['date']
            time = request.form['time']
            
            # --- Advanced Pre-Flight Validation ---
            from datetime import datetime
            time_obj = datetime.strptime(time, '%H:%M').time()
            if not (datetime.strptime('09:00', '%H:%M').time() <= time_obj <= datetime.strptime('21:00', '%H:%M').time()):
                flash('Hospital operates strictly from 9 AM to 9 PM. Please select a valid time.', 'error')
                return redirect(url_for('manage_appointments'))

            # Check Doctor Leaves
            is_on_leave = db.fetch_all("SELECT 1 FROM DoctorLeaves WHERE DoctorID=%s AND LeaveDate=%s", (d_id, date))
            if is_on_leave:
                flash('The Doctor is officially marked on leave for this date. Please select another date.', 'error')
                return redirect(url_for('manage_appointments'))

            # Check 30-Minute Time Collision Lock
            collisions = db.fetch_all("""
                SELECT 1 FROM Appointments 
                WHERE DoctorID=%s AND AppointmentDate=%s AND Status != 'Cancelled'
                AND ABS(TIMESTAMPDIFF(MINUTE, AppointmentTime, STR_TO_DATE(%s, '%H:%i'))) < 30
            """, (d_id, date, time))

            if collisions:
                flash('Time slot not available, please select a time slot of after half an hour.', 'error')
                return redirect(url_for('manage_appointments'))
            
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

@app.route('/appointments/edit/<int:id>', methods=['POST'])
def edit_appointment(id):
    date = request.form['date']
    time = request.form['time']
    
    appt = db.fetch_all("SELECT DoctorID FROM Appointments WHERE AppointmentID=%s", (id,))
    if appt:
        d_id = appt[0]['DoctorID']
        from datetime import datetime
        time_obj = datetime.strptime(time, '%H:%M').time()
        if not (datetime.strptime('09:00', '%H:%M').time() <= time_obj <= datetime.strptime('21:00', '%H:%M').time()):
            flash('Hospital operates strictly from 9 AM to 9 PM.', 'error')
            return redirect(url_for('manage_appointments'))

        is_on_leave = db.fetch_all("SELECT 1 FROM DoctorLeaves WHERE DoctorID=%s AND LeaveDate=%s", (d_id, date))
        if is_on_leave:
            flash('The Doctor is officially marked on leave for this rescheduled date.', 'error')
            return redirect(url_for('manage_appointments'))

        collisions = db.fetch_all("""
            SELECT 1 FROM Appointments 
            WHERE DoctorID=%s AND AppointmentDate=%s AND Status != 'Cancelled' AND AppointmentID != %s
            AND ABS(TIMESTAMPDIFF(MINUTE, AppointmentTime, STR_TO_DATE(%s, '%H:%i'))) < 30
        """, (d_id, date, id, time))

        if collisions:
            flash('Time slot not available, please select a time slot of after half an hour.', 'error')
            return redirect(url_for('manage_appointments'))

    # Minimal reschedule (Does not trigger ACIDs in SP, pure update)
    query = "UPDATE Appointments SET AppointmentDate=%s, AppointmentTime=%s WHERE AppointmentID=%s"
    if db.execute_query(query, (date, time, id)):
        flash('Appointment rescheduled successfully!', 'success')
    else:
        flash('Failed to reschedule appointment.', 'error')
    return redirect(url_for('manage_appointments'))

@app.route('/appointments/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    if db.execute_query("DELETE FROM Appointments WHERE AppointmentID=%s", (id,)):
        flash('Appointment permanently deleted.', 'success')
    else:
        flash('Failed to delete appointment.', 'error')
    return redirect(url_for('manage_appointments'))

# --- Prescriptions Management ---
@app.route('/prescriptions', methods=['GET', 'POST'])
def manage_prescriptions():
    if request.method == 'POST':
        appt_id = request.form['appointment_id']
        med_name = request.form['medication_name']
        dosage = request.form['dosage']
        instructions = request.form['instructions']
        
        # Anti-Duplication Engine
        duplicate = db.fetch_all("SELECT 1 FROM Prescriptions WHERE AppointmentID=%s AND MedicationName=%s", (appt_id, med_name))
        if duplicate:
            flash('ERROR: Exact medication already prescribed for this Appointment.', 'error')
            return redirect(url_for('manage_prescriptions'))
            
        query = "INSERT INTO Prescriptions (AppointmentID, MedicationName, Dosage, Instructions) VALUES (%s, %s, %s, %s)"
        if db.execute_query(query, (appt_id, med_name, dosage, instructions)):
            flash('Prescription added successfully!', 'success')
        else:
            flash('Failed to add prescription.', 'error')
        return redirect(url_for('manage_prescriptions'))
        
    prescriptions = db.fetch_all('''
        SELECT pr.PrescriptionID, pr.MedicationName, pr.Dosage, pr.Instructions,
               a.AppointmentDate,
               p.FirstName as PFName, p.LastName as PLName,
               d.FirstName as DFName, d.LastName as DLName
        FROM Prescriptions pr
        JOIN Appointments a ON pr.AppointmentID = a.AppointmentID
        JOIN Patients p ON a.PatientID = p.PatientID
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        ORDER BY pr.PrescriptionID DESC
    ''')
    
    appointments = db.fetch_all('''
        SELECT a.AppointmentID, a.AppointmentDate, p.FirstName, p.LastName, d.LastName as DLastName
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        WHERE a.Status != 'Cancelled'
        ORDER BY a.AppointmentDate DESC
    ''')
    
    return render_template('prescription.html', prescriptions=prescriptions, appointments=appointments)

@app.route('/prescriptions/edit/<int:id>', methods=['POST'])
def edit_prescription(id):
    med_name = request.form['medication_name']
    dosage = request.form['dosage']
    instructions = request.form['instructions']
    query = "UPDATE Prescriptions SET MedicationName=%s, Dosage=%s, Instructions=%s WHERE PrescriptionID=%s"
    if db.execute_query(query, (med_name, dosage, instructions, id)):
        flash('Prescription updated successfully!', 'success')
    else:
        flash('Failed to update prescription.', 'error')
    return redirect(url_for('manage_prescriptions'))

@app.route('/prescriptions/delete/<int:id>', methods=['POST'])
def delete_prescription(id):
    if db.execute_query("DELETE FROM Prescriptions WHERE PrescriptionID=%s", (id,)):
        flash('Prescription permanently deleted.', 'success')
    else:
        flash('Failed to delete prescription.', 'error')
    return redirect(url_for('manage_prescriptions'))

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

@app.route('/billing/edit/<int:id>', methods=['POST'])
def edit_billing(id):
    amount = request.form.get('amount')
    status = request.form.get('status')
    if amount and status:
        query = "UPDATE Billing SET Amount=%s, PaymentStatus=%s WHERE BillID=%s"
        if db.execute_query(query, (amount, status, id)):
            flash('Bill updated successfully!', 'success')
        else:
            flash('Failed to update bill.', 'error')
    return redirect(url_for('manage_billing'))

@app.route('/billing/delete/<int:id>', methods=['POST'])
def delete_billing(id):
    if db.execute_query("DELETE FROM Billing WHERE BillID=%s", (id,)):
        flash('Bill permanently deleted.', 'success')
    else:
        flash('Failed to delete bill.', 'error')
    return redirect(url_for('manage_billing'))

# --- Medical History ---
@app.route('/history', methods=['GET', 'POST'])
def view_history():
    if request.method == 'POST':
        p_id = request.form['patient_id']
        d_id = request.form['doctor_id']
        diag = request.form['diagnosis']
        treat = request.form['treatment']
        
        # Anti-Duplication Engine 
        duplicate = db.fetch_all("SELECT 1 FROM MedicalHistory WHERE PatientID=%s AND DoctorID=%s AND Diagnosis=%s AND Treatment=%s AND DATE(DateRecorded) = CURDATE()", (p_id, d_id, diag, treat))
        if duplicate:
            flash('ERROR: Exact identical diagnosis & treatment already recorded against this patient today.', 'error')
            return redirect(url_for('view_history'))
            
        query = "INSERT INTO MedicalHistory (PatientID, DoctorID, Diagnosis, Treatment) VALUES (%s, %s, %s, %s)"
        if db.execute_query(query, (p_id, d_id, diag, treat)):
            flash('Medical record added successfully.', 'success')
        else:
            flash('Failed to add record.', 'error')
        return redirect(url_for('view_history'))

    records = db.fetch_all('''
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
    return render_template('history.html', records=records, patients=patients, doctors=doctors)

@app.route('/history/edit/<int:id>', methods=['POST'])
def edit_history(id):
    diag = request.form['diagnosis']
    treat = request.form['treatment']
    query = "UPDATE MedicalHistory SET Diagnosis=%s, Treatment=%s WHERE RecordID=%s"
    if db.execute_query(query, (diag, treat, id)):
        flash('Medical record updated successfully!', 'success')
    else:
        flash('Failed to update medical record.', 'error')
    return redirect(url_for('view_history'))

@app.route('/history/delete/<int:id>', methods=['POST'])
def delete_history(id):
    if db.execute_query("DELETE FROM MedicalHistory WHERE RecordID=%s", (id,)):
        flash('Medical record permanently deleted.', 'success')
    else:
        flash('Failed to delete medical record.', 'error')
    return redirect(url_for('view_history'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
