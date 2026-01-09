-- Database Schema for Automated Pharmacy System

DROP DATABASE IF EXISTS pharmacy_db;
CREATE DATABASE pharmacy_db;
USE pharmacy_db;

-- Users Table (Doctors and Pharmacists)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- In production, use hashing. For hackathon, plain text/simple hash is acceptable strictly per constraints
    role ENUM('doctor', 'pharmacist', 'admin') NOT NULL,
    full_name VARCHAR(100)
);

-- ... (skipping unchanged tables) ...

-- Seed Data
INSERT INTO users (username, email, password, role, full_name) VALUES 
('admin', 'admin@medihub.com', 'pass123', 'admin', 'System Admin'),
('doc1', 'doctor@medihub.com', 'pass123', 'doctor', 'Dr. Smith'),
('pharm1', 'pharmacy@medihub.com', 'pass123', 'pharmacist', 'Pharma. Jones');

INSERT INTO medicines (name, quantity, price) VALUES 
('Paracetamol 500mg', 1000, 5.00),
('Amoxicillin 500mg', 500, 12.50),
('Ibuprofen 400mg', 800, 8.00),
('Cetirizine 10mg', 600, 3.00),
('Aspirin 75mg', 400, 4.50),
('Metformin 500mg', 1000, 2.50),
('Atorvastatin 20mg', 700, 15.00),
('Omeprazole 20mg', 600, 6.00),
('Azithromycin 500mg', 300, 45.00),
('Pantoprazole 40mg', 800, 7.00),
('Diclofenac 50mg', 500, 4.00);
