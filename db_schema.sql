-- Hospital Patient Management System - Enhanced Database Schema & Pre-Filled Mock Data

DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db;
USE hospital_db;

-- ==========================================
-- 1. Patients Table
-- ==========================================
CREATE TABLE IF NOT EXISTS Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DOB DATE NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    ContactNumber VARCHAR(15) NOT NULL,
    Address TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. Doctors Table
-- ==========================================
CREATE TABLE IF NOT EXISTS Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Specialization VARCHAR(100) NOT NULL,
    ContactNumber VARCHAR(15) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL
);

-- ==========================================
-- 3. Appointments Table
-- ==========================================
CREATE TABLE IF NOT EXISTS Appointments (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE
);

-- ==========================================
-- 4. Medical History Table
-- ==========================================
CREATE TABLE IF NOT EXISTS MedicalHistory (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    Diagnosis TEXT NOT NULL,
    Treatment TEXT NOT NULL,
    DateRecorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE
);

-- ==========================================
-- 5. Prescriptions Table
-- ==========================================
CREATE TABLE IF NOT EXISTS Prescriptions (
    PrescriptionID INT AUTO_INCREMENT PRIMARY KEY,
    AppointmentID INT NOT NULL,
    MedicationName VARCHAR(100) NOT NULL,
    Dosage VARCHAR(50) NOT NULL,
    Instructions TEXT,
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID) ON DELETE CASCADE
);

-- ==========================================
-- 6. Billing Table
-- ==========================================
CREATE TABLE IF NOT EXISTS Billing (
    BillID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    AppointmentID INT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    DateIssued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentStatus ENUM('Pending', 'Paid', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID) ON DELETE SET NULL
);

-- ==========================================================
-- PL/SQL Elements (MySQL Stored Procedures & Triggers)
-- ==========================================================
DELIMITER //

-- STORED PROCEDURE: Book Appointment safely using Transactions
CREATE PROCEDURE BookAppointment (
    IN p_PatientID INT,
    IN p_DoctorID INT,
    IN p_ApptDate DATE,
    IN p_ApptTime TIME,
    OUT p_Message VARCHAR(100)
)
BEGIN
    DECLARE clash_count INT;
    START TRANSACTION;
    
    SELECT COUNT(*) INTO clash_count 
    FROM Appointments 
    WHERE DoctorID = p_DoctorID 
      AND AppointmentDate = p_ApptDate 
      AND AppointmentTime = p_ApptTime 
      AND Status != 'Cancelled';
      
    IF clash_count > 0 THEN
        SET p_Message = 'Error: Doctor is already booked at this time.';
        ROLLBACK;
    ELSE
        INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status)
        VALUES (p_PatientID, p_DoctorID, p_ApptDate, p_ApptTime, 'Scheduled');
        SET p_Message = 'Appointment booked successfully.';
        COMMIT;
    END IF;
END //

-- TRIGGER: Auto-Generate Pending Bill after Appointment is Completed
CREATE TRIGGER AfterAppointmentComplete
AFTER UPDATE ON Appointments
FOR EACH ROW
BEGIN
    IF NEW.Status = 'Completed' AND OLD.Status != 'Completed' THEN
        INSERT INTO Billing (PatientID, AppointmentID, Amount, PaymentStatus)
        VALUES (NEW.PatientID, NEW.AppointmentID, 850.00, 'Pending');
    END IF;
END //

DELIMITER ;

-- ==========================================================
-- SAMPLE DATA INSERTION (RICH PRE-DATA)
-- ==========================================================

-- Insert Doctors (Extensive Mock Data)
INSERT INTO Doctors (FirstName, LastName, Specialization, ContactNumber, Email) VALUES
('Arun', 'Sharma', 'Cardiologist', '9876543210', 'arun.sharma@caresync.com'),
('Priya', 'Mehta', 'Neurologist', '8765432109', 'priya.mehta@caresync.com'),
('Rohan', 'Desai', 'Orthopedic Surgeon', '7654321098', 'rohan.desai@caresync.com'),
('Kavita', 'Singh', 'Pediatrician', '6543210987', 'kavita.singh@caresync.com'),
('Vikram', 'Patil', 'Dermatologist', '5432109876', 'vikram.patil@caresync.com'),
('Neha', 'Verma', 'General Physician', '4321098765', 'neha.verma@caresync.com');

-- Insert Patients (Extensive Mock Data)
INSERT INTO Patients (FirstName, LastName, DOB, Gender, ContactNumber, Address) VALUES
('Rahul', 'Joshi', '1985-04-12', 'Male', '9123456780', '14 MG Road, Corel Appt, Pune, Maharashtra'),
('Anjali', 'Nair', '1992-08-25', 'Female', '9234567891', '102 Sunrise Towers, Koregaon Park, Pune'),
('Sunil', 'Gavaskar', '1960-03-10', 'Male', '9345678902', 'Sector 5, FC Road, Pune'),
('Maya', 'Bhide', '2015-11-05', 'Female', '9456789013', 'House 44, Kothrud, Pune, Maharashtra'),
('Amit', 'Thakur', '1978-01-20', 'Male', '9567890124', 'Flat 12, Shivaji Nagar, Pune'),
('Sneha', 'Kapoor', '1995-12-18', 'Female', '9678901235', 'Green Fields Society, Baner, Pune'),
('Manoj', 'Tiwari', '1980-07-07', 'Male', '9789012346', 'Blue Skies Bldg, Viman Nagar, Pune');

-- Insert historical Appointments (Mostly Completed, Some Scheduled/Cancelled)
INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status) VALUES
(1, 1, '2026-01-15', '10:00:00', 'Completed'),
(2, 2, '2026-01-22', '11:00:00', 'Completed'),
(3, 3, '2026-02-10', '09:30:00', 'Completed'),
(4, 4, '2026-02-18', '14:00:00', 'Completed'),
(5, 5, '2026-02-28', '16:00:00', 'Completed'),
(6, 6, '2026-03-01', '10:30:00', 'Completed'),
(1, 1, '2026-04-16', '10:00:00', 'Scheduled'),
(7, 2, '2026-04-18', '15:00:00', 'Scheduled'),
(3, 2, '2026-04-01', '09:00:00', 'Cancelled');

-- Insert Medical History (Rich mock context)
INSERT INTO MedicalHistory (PatientID, DoctorID, Diagnosis, Treatment, DateRecorded) VALUES
(1, 1, 'Mild Hypertension and elevated cholesterol.', 'Prescribed daily walking 45 mins, low sodium diet, and Atorvastatin 10mg.', '2023-11-10 10:30:00'),
(2, 2, 'Frequent tension headaches due to stress and posture.', 'Ergonomic workspace setup, Amitriptyline 10mg at night if severe.', '2023-11-12 11:30:00'),
(3, 3, 'Osteoarthritis in right knee. Cartilage wear observed.', 'Physical therapy recommended. Non-surgical approach planned. Diclofenac gel applied.', '2023-11-15 10:00:00'),
(4, 4, 'Viral Fever and mild throat infection.', 'Complete rest, paracetamol for fever peaks, plenty of warm fluids.', '2023-11-18 14:15:00'),
(5, 5, 'Eczema flare-up on forearms.', 'Hydrocortisone cream 1% topical, moisturizing regularly with cetaphil.', '2023-11-20 16:20:00'),
(6, 6, 'Acute gastroenteritis. Mild dehydration.', 'ORS solution 1 litre a day, soft diet. Avoid dairy and sugar for 3 days.', '2023-12-05 11:00:00');

-- Insert Prescriptions 
INSERT INTO Prescriptions (AppointmentID, MedicationName, Dosage, Instructions) VALUES
(1, 'Atorvastatin', '10mg', '1 pill at night after dinner'),
(2, 'Amitriptyline', '10mg', 'Take 1 pill at night before bed only if pain exists'),
(3, 'Diclofenac Gel', '1%', 'Apply gently on knee twice a day'),
(4, 'Paracetamol', '500mg', 'If fever crosses 100 F, take 1 dose'),
(5, 'Hydrocortisone', '1% cream', 'Apply thin layer on affected areas twice daily'),
(6, 'Electral ORS', '1 Sachet', 'Mix in 1 litre water and sip throughout day');

-- Insert Billing (Historical paid and recent pending bills)
INSERT INTO Billing (PatientID, AppointmentID, Amount, DateIssued, PaymentStatus) VALUES
(1, 1, 850.00, '2023-11-10 10:35:00', 'Paid'),
(2, 2, 1000.00, '2023-11-12 11:35:00', 'Paid'),
(3, 3, 1200.00, '2023-11-15 10:05:00', 'Paid'),
(4, 4, 600.00, '2023-11-18 14:20:00', 'Paid'),
(5, 5, 850.00, '2023-11-20 16:25:00', 'Pending'),
(6, 6, 750.00, '2023-12-05 11:05:00', 'Pending');

