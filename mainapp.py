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
           
            return redirect(url_for('signIn'))
        except sqlite3.IntegrityError as e:
            conn.close()
          
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
    programs = getHealthPrograms()
   
    conn.close()

    return render_template('dashboard.html', doctor_data=doctor,stats =clients, clients=clients,programs=programs)

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

@app.route('/enroll', methods=['GET', 'POST'])
def enroll_client():
    if request.method == 'POST':
        program_id = request.form['program_id']
        national_id = request.form['national_id']

        # Get client details by National ID
        conn = get_db_connection()
        client_query = 'SELECT * FROM clients WHERE id = ?'
        client = conn.execute(client_query, (national_id,)).fetchone()

        if client:
            # Enroll client in the program
            doctor_id = 1  # Assuming doctor is logged in, replace with actual logged-in doctor id
            enrollment_date = request.form['enrollment_date']
            conn.execute('''
            INSERT INTO program_enrollments (client_id, program_id, enrolled_by, enrollment_date)
            VALUES (?, ?, ?, ?)
            ''', (client['id'], program_id, doctor_id, enrollment_date))
            conn.commit()
            conn.close()

            return redirect(url_for('enrollment_success'))
        else:
            return "Client not found", 404

    else:
        # Fetch all programs and clients
        conn = get_db_connection()
        programs = conn.execute('SELECT * FROM health_programs').fetchall()
        clients = conn.execute('SELECT * FROM clients').fetchall()
        conn.close()
        return render_template('enroll_client.html', programs=programs, clients=clients)

@app.route('/enrollment_success')
def enrollment_success():
    return "Client successfully enrolled to the program!"

@app.route('/view-clients', methods=['GET'])
def view_clients():
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()

    return render_template('clients.html', clients=clients)

@app.route('/client_info/<int:national_id>', methods=['GET'])
def client_info(national_id):
    conn = get_db_connection()
    client_query = 'SELECT * FROM clients WHERE id = ?'
    client = conn.execute(client_query, (national_id,)).fetchone()
    conn.close()

    if client:
        return jsonify({
            'client': {
                'first_name': client['first_name'],
                'last_name': client['last_name'],
                'date_of_birth': client['date_of_birth'],
                'gender': client['gender'],
                'email': client['email'],
                'address': client['address']
            }
        })
    else:
        return jsonify({'client': None})

@app.route('/client/<int:client_id>', methods=['GET'])
def view_client(client_id):
    conn = get_db_connection()

    # Get client details
    client_query = 'SELECT * FROM clients WHERE id = ?'
    client = conn.execute(client_query, (client_id,)).fetchone()

    # Get the programs the client is enrolled in
    enrollments_query = '''
    SELECT health_programs.name, health_programs.start_date, health_programs.end_date, program_enrollments.status
    FROM program_enrollments
    JOIN health_programs ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    enrollments = conn.execute(enrollments_query, (client_id,)).fetchall()

    # Get milestones related to the programs the client is enrolled in
    milestones_query = '''
    SELECT program_milestones.title, program_milestones.target_date, program_milestones.description
    FROM program_milestones
    JOIN health_programs ON program_milestones.program_id = health_programs.id
    JOIN program_enrollments ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    milestones = conn.execute(milestones_query, (client_id,)).fetchall()

    # Get resources related to the programs the client is enrolled in
    resources_query = '''
    SELECT program_resources.resource_type, program_resources.quantity
    FROM program_resources
    JOIN health_programs ON program_resources.program_id = health_programs.id
    JOIN program_enrollments ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    resources = conn.execute(resources_query, (client_id,)).fetchall()

    conn.close()

    return render_template('view_client.html', client=client, enrollments=enrollments, milestones=milestones, resources=resources)


@app.route('/client/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    db = get_db_connection()

    # Delete the client from the database
    db.execute('''
        DELETE FROM clients WHERE id = ?
    ''', (client_id,))
    db.commit()

    return redirect(url_for('dashboard'))

    

@app.route('/add-program', methods=['GET', 'POST'])
def add_new_health_program():
    if request.method == 'GET':
        return render_template('newProgram.html')
    if request.method == 'POST':
      
        try:
            # Extract base program info
            name = request.form['programName']
            description = request.form['description']
            program_type = request.form['programType']
            start_date = request.form['startDate']
            end_date = request.form['endDate']
            target_group = request.form['targetGroup']
            estimated_clients = request.form['estimatedClients']
            require_referral = 'requireReferral' in request.form
            follow_up = 'followUp' in request.form
            conn = get_db_connection()
            cursor = conn.cursor()
            # Insert into health_programs
            cursor.execute("""
                INSERT INTO health_programs 
                (name, description, program_type, start_date, end_date, target_group, estimated_clients, require_referral, follow_up)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, program_type, start_date, end_date, target_group, estimated_clients, require_referral, follow_up))
            program_id = cursor.lastrowid
            # Milestones
            milestone_titles = request.form.getlist('milestone_title[]')
            milestone_dates = request.form.getlist('milestone_date[]')
            milestone_descriptions = request.form.getlist('milestone_description[]')

            for title, date, desc in zip(milestone_titles, milestone_dates, milestone_descriptions):
                cursor.execute("""
                    INSERT INTO program_milestones (program_id, title, target_date, description)
                    VALUES (?, ?, ?, ?)
                """, (program_id, title, date, desc))

            # Resources
            resource_types = request.form.getlist('resource_type[]')
            resource_quantities = request.form.getlist('resource_quantity[]')

            for rtype, qty in zip(resource_types, resource_quantities):
                cursor.execute("""
                    INSERT INTO program_resources (program_id, resource_type, quantity)
                    VALUES (?, ?, ?)
                """, (program_id, rtype, qty))

            conn.commit()
            return redirect(url_for('dashboard'))

        except Exception as e:
            return "An error occurred while creating the program.", 500

def getHealthPrograms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_programs')
    programs = cursor.fetchall()
    conn.close()
    return [dict(program) for program in programs]

@app.route('/programs')
def list_programs():
    db = get_db_connection()
    programs = db.execute('SELECT * FROM health_programs').fetchall()
    return render_template('programs.html', programs=programs)

@app.route('/program/<int:program_id>/edit')
def edit_program(program_id):
    db = get_db_connection()
    
    # Fetch program details
    program = db.execute('''
        SELECT p.*, d.first_name || ' ' || d.last_name AS created_by_name
        FROM health_programs p
        LEFT JOIN doctors d ON p.created_by = d.id
        WHERE p.id = ?
    ''', (program_id,)).fetchone()

    if not program:
        return "Program not found", 404

    # Fetch milestones
    milestones = db.execute('''
        SELECT * FROM program_milestones WHERE program_id = ?
    ''', (program_id,)).fetchall()

    # Fetch resources
    resources = db.execute('''
        SELECT * FROM program_resources WHERE program_id = ?
    ''', (program_id,)).fetchall()

    return render_template('edit_program.html', program=program, milestones=milestones, resources=resources)



@app.route('/program/<int:program_id>')
def view_program(program_id):
    db = get_db_connection()
    
    # Fetch program details
    program = db.execute('''
        SELECT p.*, d.first_name || ' ' || d.last_name AS created_by_name
        FROM health_programs p
        LEFT JOIN doctors d ON p.created_by = d.id
        WHERE p.id = ?
    ''', (program_id,)).fetchone()

    if not program:
        return "Program not found", 404

    # Fetch milestones
    milestones = db.execute('''
        SELECT * FROM program_milestones WHERE program_id = ?
    ''', (program_id,)).fetchall()

    # Fetch resources
    resources = db.execute('''
        SELECT * FROM program_resources WHERE program_id = ?
    ''', (program_id,)).fetchall()

    # Count enrolled clients
    enrolled_clients = db.execute('''
        SELECT COUNT(*) as count FROM program_enrollments WHERE program_id = ?
    ''', (program_id,)).fetchone()['count']

    return render_template('program_detail.html',
                           program=program,
                           milestones=milestones,
                           resources=resources,
                           enrolled_clients=enrolled_clients)

@app.route('/program/<int:program_id>/delete', methods=['POST'])
def delete_program(program_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM health_programs WHERE id = ?', (program_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Program deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#Update program
@app.route('/program/<int:program_id>/update', methods=['POST'])
def update_program(program_id):
    
    name = request.form['name']
    description = request.form['description']
    program_type = request.form['program_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    target_group = request.form['target_group']
    estimated_clients = request.form['estimated_clients']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE health_programs
            SET name=?, description=?, program_type=?, start_date=?, end_date=?, target_group=?, estimated_clients=?
            WHERE id=?
        """, (name, description, program_type, start_date, end_date, target_group, estimated_clients, program_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Program updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
