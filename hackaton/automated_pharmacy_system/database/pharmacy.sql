-- Database Schema for Automated Pharmacy System

DROP DATABASE IF EXISTS pharmacy_db;
CREATE DATABASE pharmacy_db;
USE pharmacy_db;

-- Users Table (Doctors and Pharmacists)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- In production, use hashing. For hackathon, plain text/simple hash is acceptable strictly per constraints
    role ENUM('doctor', 'pharmacist') NOT NULL,
    full_name VARCHAR(100)
);

-- Patients Table
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    allergies TEXT,
    contact VARCHAR(20)
);

-- Medicines Table (Inventory)
CREATE TABLE medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL
);

-- Prescriptions Table
CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'validated', 'dispensed') DEFAULT 'pending',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES users(user_id)
);

-- Prescription Details (Medicines in a prescription)
CREATE TABLE prescription_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT,
    medicine_id INT, 
    dosage VARCHAR(100), -- e.g., "1-0-1 after food"
    days INT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

-- Billing Table
CREATE TABLE billing (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT UNIQUE,
    total_amount DECIMAL(10, 2),
    payment_status ENUM('Unpaid', 'Paid') DEFAULT 'Unpaid',
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
);

-- Seed Data
INSERT INTO users (username, password, role, full_name) VALUES 
('doc1', 'pass123', 'doctor', 'Dr. Smith'),
('pharm1', 'pass123', 'pharmacist', 'Pharma. Jones');

INSERT INTO medicines (name, quantity, price) VALUES 
('Paracetamol 500mg', 1000, 5.00),
('Amoxicillin 500mg', 500, 12.50),
('Ibuprofen 400mg', 800, 8.00),
('Cetirizine 10mg', 600, 3.00),
('Aspirin 75mg', 400, 4.50);
