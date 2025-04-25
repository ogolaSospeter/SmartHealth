import os
from flask import Flask, redirect, request, jsonify, render_template, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import sqlite3

load_dotenv()

def get_db_connection():
    conn = sqlite3.connect('smarthealthdatabase.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('landing.html')
@app.route('/register-doctor', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        print("The received data from the form is: ", request.form)
        # Get form data directly from the request form
        license_number = request.form['licenseNumber']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phoneNumber']
        specialty = request.form['specialty']
        address = request.form['address']
        city = request.form['city']
        year_of_experience = request.form['experience']

        # Hash the password
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO doctors (license_number, first_name, last_name, email, password, phone_number, specialty, address, year_of_experience,city)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (license_number, first_name, last_name, email, hashed_password, phone, specialty, address, year_of_experience,city))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            print('Registration successful! You can now log in.')
            return redirect(url_for('signIn'))
        except sqlite3.IntegrityError as e:
            conn.close()
            print('Error:', e)
            flash('Email or license number already exists. Please try again.', 'danger')
            return redirect(url_for('signUp'))

    return render_template('signUp.html')

# ----- SIGNIN (DOCTOR LOGIN) -----
@app.route('/signin', methods=['GET', 'POST'])
def signIn():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM doctors WHERE email = ?', (email,))
        doctor = cursor.fetchone()
        conn.close()
        if doctor and check_password_hash(doctor['password'], password): 
            session['user_id'] = doctor['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  
        elif doctor and not check_password_hash(doctor['password'], password):
            flash('Incorrect Username or password. Please try again.', 'danger')
            return redirect(url_for('signIn'))
        else:
            flash("User not found. Please sign up.", 'danger')
            return redirect(url_for('signIn'))

    return render_template('signIn.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('signIn'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctors WHERE id = ?', (session['user_id'],))
    doctor = cursor.fetchone()
    clients = fetch_all_clients()
    print("The clients data is: ", clients)

    conn.close()

    return render_template('dashboard.html', doctor_data=doctor,stats =clients, clients=clients)


def fetch_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return [dict(client) for client in clients]

@app.route('/add-new-client', methods=['POST'])
def add_new_client():
    data = request.get_json()
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    gender = data.get('gender')
    contact_number = data.get('contact_number')
    email = data.get('email')
    address = data.get('address')
    print("The received client data from the form is: ", data)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (
                first_name, last_name, date_of_birth, gender, contact_number, email, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, date_of_birth, gender, contact_number, email, address))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Client added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#Get all clients
@app.route('/get-clients', methods=['GET'])
def get_clients():
    return jsonify(fetch_all_clients()), 200





@app.route('/add-program', methods=['GET', 'POST'])
def add_new_health_program():
    if request.method == 'GET':
        return render_template('newProgram.html')
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        program_type = data.get('program_type')
        start_date = data.get('start_date')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO health_programs (name, description, program_type, start_date)
                VALUES (?, ?, ?, ?)
            """, (name, description, program_type, start_date))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Health program added successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        


if __name__ == '__main__':
    app.run(debug=True)
