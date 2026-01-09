from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'hackathon_secret_key' # Change for production

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',      # Default XAMPP/MySQL user
    'password': '123456',      # Default XAMPP/MySQL password (empty)
    'database': 'pharmacy_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif session['role'] == 'pharmacist':
            return redirect(url_for('pharmacist_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials')
        else:
            flash('Database connection failed')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Database Error"
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY patient_id DESC")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('doctor_dashboard.html', patients=patients, medicines=medicines)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    contact = request.form['contact']
    allergies = request.form['allergies']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (name, age, gender, contact, allergies) VALUES (%s, %s, %s, %s, %s)", 
                   (name, age, gender, contact, allergies))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Patient added successfully!')
    return redirect(url_for('doctor_dashboard'))

@app.route('/create_prescription', methods=['POST'])
def create_prescription():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    patient_id = request.form['patient_id']
    medicine_id = request.form['medicine_id']
    dosage = request.form['dosage']
    days = request.form['days']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Prescription Record
    cursor.execute("INSERT INTO prescriptions (patient_id, doctor_id, date) VALUES (%s, %s, NOW())", 
                   (patient_id, session['user_id']))
    prescription_id = cursor.lastrowid
    
    # Add Medicine Details (Hackathon simplification: 1 medicine per prescription for speed, or handle multiple if UI allows)
    # The prompt implies "prescription_details" table. I'll add one item.
    cursor.execute("INSERT INTO prescription_details (prescription_id, medicine_id, dosage, days) VALUES (%s, %s, %s, %s)",
                   (prescription_id, medicine_id, dosage, days))
    
    conn.commit()
    cursor.close()
    conn.close()
    flash('Prescription created!')
    return redirect(url_for('doctor_dashboard'))

@app.route('/pharmacist_dashboard', methods=['GET'])
def pharmacist_dashboard():
    if 'user_id' not in session or session['role'] != 'pharmacist':
        return redirect(url_for('login'))
    
    prescription = None
    details = None
    bill = None
    
    prescription_id = request.args.get('prescription_id')
    
    if prescription_id:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch Basic Prescription Info
        query = """
            SELECT p.prescription_id, p.date, p.status, pat.name as patient_name, u.full_name as doctor_name
            FROM prescriptions p
            JOIN patients pat ON p.patient_id = pat.patient_id
            JOIN users u ON p.doctor_id = u.user_id
            WHERE p.prescription_id = %s
        """
        cursor.execute(query, (prescription_id,))
        prescription = cursor.fetchone()
        
        if prescription:
            # Fetch Medicines
            det_query = """
                SELECT pd.*, m.name as medicine_name, m.price, m.quantity as stock
                FROM prescription_details pd
                JOIN medicines m ON pd.medicine_id = m.medicine_id
                WHERE pd.prescription_id = %s
            """
            cursor.execute(det_query, (prescription_id,))
            details = cursor.fetchall()
            
            # Fetch Bill if exists
            cursor.execute("SELECT * FROM billing WHERE prescription_id = %s", (prescription_id,))
            bill = cursor.fetchone()
            
        cursor.close()
        conn.close()
        
    return render_template('pharmacist_dashboard.html', prescription=prescription, details=details, bill=bill)

@app.route('/validate_prescription/<int:p_id>', methods=['POST'])
def validate_prescription(p_id):
    if 'user_id' not in session or session['role'] != 'pharmacist':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Update Inventory (Basic decrementation logic)
    # Get items
    cursor.execute("SELECT medicine_id, days FROM prescription_details WHERE prescription_id = %s", (p_id,))
    items = cursor.fetchall()
    
    for item in items:
        # Assuming quantity to deduct = days (Hackathon simplification)
        qty_to_deduct = item['days'] 
        cursor.execute("UPDATE medicines SET quantity = quantity - %s WHERE medicine_id = %s", (qty_to_deduct, item['medicine_id']))
        
    # 2. Update Status
    cursor.execute("UPDATE prescriptions SET status = 'validated' WHERE prescription_id = %s", (p_id,))
    
    # 3. Calculate Bill
    # Total = Sum(Price * Days)
    cursor.execute("""
        SELECT SUM(m.price * pd.days) as total 
        FROM prescription_details pd 
        JOIN medicines m ON pd.medicine_id = m.medicine_id 
        WHERE pd.prescription_id = %s
    """, (p_id,))
    result = cursor.fetchone()
    total_amount = result['total'] if result['total'] else 0
    
    # 4. Create Bill
    cursor.execute("INSERT INTO billing (prescription_id, total_amount, payment_status) VALUES (%s, %s, 'Unpaid')", 
                   (p_id, total_amount))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Prescription validated and bill generated.')
    return redirect(url_for('pharmacist_dashboard', prescription_id=p_id))

@app.route('/pay_bill/<int:bill_id>')
def pay_bill(bill_id):
    if 'user_id' not in session or session['role'] != 'pharmacist':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE billing SET payment_status = 'Paid' WHERE bill_id = %s", (bill_id,))
    
    # Get prescription ID to redirect back
    cursor.execute("SELECT prescription_id FROM billing WHERE bill_id = %s", (bill_id,))
    res = cursor.fetchone()
    p_id = res[0]
    
    # Update prescription status to dispensed
    cursor.execute("UPDATE prescriptions SET status = 'dispensed' WHERE prescription_id = %s", (p_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    flash('Payment recorded successfully.')
    return redirect(url_for('pharmacist_dashboard', prescription_id=p_id))

@app.route('/invoice/<int:bill_id>')
def invoice(bill_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch Bill
    cursor.execute("SELECT * FROM billing WHERE bill_id = %s", (bill_id,))
    bill = cursor.fetchone()
    
    if not bill:
        return "Invoice not found", 404
        
    # Fetch Prescription
    cursor.execute("SELECT * FROM prescriptions WHERE prescription_id = %s", (bill['prescription_id'],))
    prescription = cursor.fetchone()
    
    # Fetch Patient
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (prescription['patient_id'],))
    patient = cursor.fetchone()
    
    # Fetch Doctor
    cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (prescription['doctor_id'],))
    doctor = cursor.fetchone()
    
    # Fetch Items
    query = """
        SELECT pd.*, m.name as medicine_name, m.price 
        FROM prescription_details pd
        JOIN medicines m ON pd.medicine_id = m.medicine_id
        WHERE pd.prescription_id = %s
    """
    cursor.execute(query, (bill['prescription_id'],))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('invoice.html', bill=bill, prescription=prescription, patient=patient, doctor=doctor, items=items)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
