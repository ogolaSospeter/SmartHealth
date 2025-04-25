"""
The import section for the libraries to be used in the project
"""
import os
from flask import Flask, redirect, request, jsonify, render_template, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

from python.Reusables import calculate_age
from security.Auth import token_required

load_dotenv()

#The get connection function to set up the connection to the database

def get_db_connection():
    conn = sqlite3.connect('smarthealthdatabase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Setting up my flask application 
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


#The endpoint to render the enrtry screen
@app.route('/')
def index():
    return render_template('landing.html')

""""
For a doctor to manage the system, the doctor must be registered on the system. 
This endpoint thereby enables a new doctor entry into the system.
The @token_required decorator is used to ensure that only authenticated users can access this endpoins.
"""
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

"""
A registered doctor can thus proceed to signin into the system
"""

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

"""
The main dashboard screen.
On this dashboard, I present the analysis of the system components
"""

@app.route('/dashboard', methods=['GET'])
def dashboard():
    
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('signIn'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch doctor data
    cursor.execute('SELECT * FROM doctors WHERE id = ?', (session['user_id'],))
    doctor = cursor.fetchone()

    clients = fetch_all_clients()
   

    # Fetch programs data
    programs = getHealthPrograms()

    # Calculate statistics
    total_clients = len(clients)
    male_clients = len([client for client in clients if client['gender'] == 'male'])
    female_clients = len([client for client in clients if client['gender'] == 'female'])
    

    age_group_18_35 = len([client for client in clients if 18 <= calculate_age(client['date_of_birth']) <= 35])
    age_group_36_50 = len([client for client in clients if 36 <= calculate_age(client['date_of_birth']) <= 50])
    age_group_51_plus = len([client for client in clients if calculate_age(client['date_of_birth']) >= 51])

    # Total active programs
    active_programs = len([program for program in programs if program['status'] == 'active'])

    conn.close()

    # Passing stats to template
    return render_template('dashboard.html', 
                           doctor_data=doctor, 
                           stats={
                               'total_clients': total_clients,
                               'male_clients': male_clients,
                               'female_clients': female_clients,
                               'age_group_18_35': age_group_18_35,
                               'age_group_36_50': age_group_36_50,
                               'age_group_51_plus': age_group_51_plus,
                               'active_programs': active_programs,
                           }, 
                           clients=clients, programs=programs)

"""
The fetch clients function is meant to get all the clients registered on the system
It then returns a dictionary
"""

def fetch_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return [dict(client) for client in clients]

"""
The function responsible for the adding of a new client to the database
"""

@app.route('/add-new-client', methods=['POST'])
@token_required
def add_new_client():
   
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    contact_number = request.form['phone_number']
    email = request.form['email']
    address = request.form['address']
    national_id = request.form['national_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (
                first_name, last_name, date_of_birth, gender, contact_number, email, address, national_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, date_of_birth, gender, contact_number, email, address, national_id))
        conn.commit()
        conn.close()
        flash("Client Successfully Registered!", "success")
        return redirect(url_for('dashboard'))
    except Exception as e:
      
        flash(f"An error occurred while adding the client, error:\n{e}", "danger")
        
"""
The enroll_client function is meant to enroll a client into a health program
The function checks if the client exists and if the program is active before enrolling the client.
This ensures that only valid enrollments are made. to programs that are active"""
@app.route('/enroll', methods=['GET', 'POST'])
@token_required
def enroll_client():
    if request.method == 'POST':
        program_id = request.form['program_id']
        national_id = request.form['national_id']

        # Get client details by National ID
        conn = get_db_connection()
        client_query = 'SELECT * FROM clients WHERE national_id = ?'
        client = conn.execute(client_query, (national_id,)).fetchone()

        if client:
            # Check if the program is active
            program_query = 'SELECT status FROM health_programs WHERE id = ?'
            program = conn.execute(program_query, (program_id,)).fetchone()

            if program and program['status'] == 'active':
                try:
                    # Enroll client in the program if the program is active
                    doctor_id = session['user_id']
                    enrollment_date = request.form['enrollment_date']
                    conn.execute('''
                    INSERT INTO program_enrollments (client_id, program_id, enrolled_by, enrollment_date)
                    VALUES (?, ?, ?, ?)
                    ''', (client['id'], program_id, doctor_id, enrollment_date))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('enrollment_success'))
                except sqlite3.IntegrityError:
                    # Handle case where client is already enrolled in the program
                    conn.close()
                    flash("Client already enrolled in this program!", "danger")
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    # Handle other exceptions
                    conn.close()
                    flash(f"An error occurred while enrolling the client: {e}", "danger")
                    return redirect(url_for('dashboard'))
            else:
                # If the program is not active, show an error
                conn.close()
                flash("The selected program already Closed!.", "danger")
                return redirect(url_for('dashboard'))
        else:
            conn.close()
            flash("Client not found", "danger")
            return redirect(url_for('enroll_client'))

    else:
        return redirect(url_for('dashboard'))


@app.route('/enrollment_success')
def enrollment_success():
    flash("Client successfully enrolled to the program!", "success")
    return redirect(url_for('dashboard'))

"""
This endpoint is meant to get the details of the client for viewing by the doctor to confirm enrollment into a program
"""
@app.route('/client/<int:client_id>', methods=['GET'])
@token_required
def view_client(client_id):
    # Instead of re-querying the database, call the get_client_profile() internally
    response = get_client_profile(client_id)

    if response[1] != 200:
        flash('Client not found or an error occurred.', 'danger')
        return redirect(url_for('dashboard'))  # Or wherever you want to redirect

    data = response[0].json  # `.json` because get_client_profile() returns a Flask Response with JSON

    client = data['client']
    enrollments = data['enrollments']
    milestones = data['milestones']
    resources = data['resources']
    print("The complete profile information is: ", data)

    return render_template('view_client.html', client=client, enrollments=enrollments, milestones=milestones, resources=resources)

"""
This endpoint is meant to get the details of the client for viewing by the doctor to confirm enrollment into a program
"""
@app.route('/client_info/<int:national_id>', methods=['GET'])
@token_required
def client_info(national_id):
    conn = get_db_connection()
    client_query = 'SELECT * FROM clients WHERE national_id = ?'
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
                'phoneNumber': client['contact_number']
            }
        })
    else:
        return jsonify({'client': None})

@app.route('/api/client/<int:client_id>', methods=['GET'])
@token_required
def get_client_profile(client_id):
    conn = get_db_connection()

    # Get client details
    client_query = 'SELECT * FROM clients WHERE id = ?'
    client = conn.execute(client_query, (client_id,)).fetchone()

    if client is None:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    """
    Retrieval of the enrollments for the client
    """
    enrollments_query = '''
    SELECT health_programs.name, health_programs.start_date, health_programs.end_date, program_enrollments.status
    FROM program_enrollments
    JOIN health_programs ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    enrollments = conn.execute(enrollments_query, (client_id,)).fetchall()

    """
    Retrieval of the milestones for the program in which the client is enrolled
    """
    milestones_query = '''
    SELECT program_milestones.title, program_milestones.target_date, program_milestones.description
    FROM program_milestones
    JOIN health_programs ON program_milestones.program_id = health_programs.id
    JOIN program_enrollments ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    milestones = conn.execute(milestones_query, (client_id,)).fetchall()

    """
    Retrieval of the resources allocated to the project in which the client is enrolled
    """
    resources_query = '''
    SELECT program_resources.resource_type, program_resources.quantity
    FROM program_resources
    JOIN health_programs ON program_resources.program_id = health_programs.id
    JOIN program_enrollments ON program_enrollments.program_id = health_programs.id
    WHERE program_enrollments.client_id = ?
    '''
    resources = conn.execute(resources_query, (client_id,)).fetchall()

    conn.close()

    # client_data ensures that the client data is returned in a dictionary format
    client_data = {
        'id': client['id'],
        'first_name': client['first_name'],
        'last_name': client['last_name'],
        'email': client['email'],
        'phone': client['contact_number']
    }

    enrollments_data = [dict(enrollment) for enrollment in enrollments]
    milestones_data = [dict(milestone) for milestone in milestones]
    resources_data = [dict(resource) for resource in resources]

    # This section builds the final json response 
    return jsonify({
        'client': client_data,
        'enrollments': enrollments_data,
        'milestones': milestones_data,
        'resources': resources_data
    }), 200

@app.route('/client/<int:client_id>/delete', methods=['POST'])
@token_required
def delete_client(client_id):
    db = get_db_connection()

    # Delete the client from the database
    db.execute('''
        DELETE FROM clients WHERE id = ?
    ''', (client_id,))
    db.commit()

    return redirect(url_for('dashboard'))

    

@app.route('/add-program', methods=['GET', 'POST'])
@token_required
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
            doctor_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()
            # Insert into health_programs
            cursor.execute("""
                INSERT INTO health_programs 
                (name, description, program_type, start_date, end_date, target_group, estimated_clients, require_referral, follow_up, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, program_type, start_date, end_date, target_group, estimated_clients, require_referral, follow_up, doctor_id))
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
            flash(f"{name} Programme has been Successfully added to the database.", "success")
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
@token_required
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
@token_required
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
@token_required
def close_program(program_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE health_programs SET status = 'closed' WHERE id = ?", (program_id,))
        conn.commit()
        conn.close()
        flash("Program Closed Successfully!", "success")
        return redirect(url_for('view_program', program_id=program_id))
    
    except Exception as e:
        flash(f"Error in updating the program status: {e}", "danger")
        return redirect(url_for('edit_program', program_id=program_id))

"""
Function to delete a program
"""
@app.route('/program/<int:program_id>/delete', methods=['POST'])
@token_required
def delete_program(program_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete all milestones and resources associated with the program
        cursor.execute("DELETE FROM program_milestones WHERE program_id = ?", (program_id,))
        cursor.execute("DELETE FROM program_resources WHERE program_id = ?", (program_id,))

        # Delete the program itself
        cursor.execute("DELETE FROM health_programs WHERE id = ?", (program_id,))

        conn.commit()
        conn.close()
        flash("Program Deleted Successfully!", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Error in deleting the program: {e}", "danger")
        return redirect(url_for('view_program', program_id=program_id))

@app.route('/program/<int:program_id>/update', methods=['POST'])
@token_required
def update_program(program_id):
    name = request.form['name']
    description = request.form['description']
    program_type = request.form['program_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    target_group = request.form['target_group']
    estimated_clients = request.form['estimated_clients']
    require_referral = 'require_referral' in request.form
    follow_up = 'follow_up' in request.form
    status = request.form['status']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the main program
        cursor.execute("""
            UPDATE health_programs
            SET name=?, description=?, program_type=?, start_date=?, end_date=?, 
                target_group=?, estimated_clients=?, require_referral=?, follow_up=?, status=?
            WHERE id=?
        """, (name, description, program_type, start_date, end_date,
              target_group, estimated_clients, int(require_referral), int(follow_up), status, program_id))

        # === Update Milestones ===
        milestone_ids = [key.split('[')[1].split(']')[0] for key in request.form if key.startswith('milestones[') and key.endswith('][id]')]
        for index in set(milestone_ids):
            milestone_id = request.form.get(f'milestones[{index}][id]')
            title = request.form.get(f'milestones[{index}][title]')
            target_date = request.form.get(f'milestones[{index}][target_date]')
            milestone_description = request.form.get(f'milestones[{index}][description]')
            cursor.execute("""
                UPDATE program_milestones
                SET title=?, target_date=?, description=?
                WHERE id=? AND program_id=?
            """, (title, target_date, milestone_description, milestone_id, program_id))

        # === Update Resources ===
        resource_ids = [key.split('[')[1].split(']')[0] for key in request.form if key.startswith('resources[') and key.endswith('][id]')]
        for index in set(resource_ids):
            resource_id = request.form.get(f'resources[{index}][id]')
            resource_type = request.form.get(f'resources[{index}][resource_type]')
            quantity = request.form.get(f'resources[{index}][quantity]')
            cursor.execute("""
                UPDATE program_resources
                SET resource_type=?, quantity=?
                WHERE id=? AND program_id=?
            """, (resource_type, quantity, resource_id, program_id))

        conn.commit()
        conn.close()
        flash("Program, Milestones, and Resources updated successfully!", "success")
        return redirect(url_for('view_program', program_id=program_id))

    except Exception as e:
        flash(f"Error in updating the program: {e}", "danger")
        return redirect(url_for('edit_program', program_id=program_id))

@app.route('/search/clients', methods=['GET'])
@token_required
def search_clients():
    search_query = request.args.get('query', '')  # Get the search query from the URL parameter

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for searching clients
    client_query = '''
        SELECT * FROM clients 
        WHERE first_name LIKE ? OR last_name LIKE ? OR national_id LIKE ? OR id LIKE ? OR email LIKE ?
    '''
    cursor.execute(client_query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    rows = cursor.fetchall()
    clients = [dict(row) for row in rows]

    conn.close()

    # Return the filtered client data as JSON
    return jsonify({'clients': clients})


@app.route('/search/programs', methods=['GET'])
@token_required
def search_programs():
    search_query = request.args.get('query', '')  # Get the search query from the URL parameter

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for searching programs
    program_query = '''
        SELECT * FROM health_programs
        WHERE name LIKE ? OR description LIKE ? OR program_type LIKE ? OR target_group LIKE ? OR id LIKE ?
    '''
    cursor.execute(program_query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}'))
    rows = cursor.fetchall()
    programs = [dict(row) for row in rows]

    conn.close()

    # Return the filtered program data as JSON
    return jsonify({'programs': programs})

@app.route('/logout')
@token_required
def signOut():
    if 'user_id' not in session:
        flash('You are not logged in.', 'danger')
        return redirect(url_for('signIn'))
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')

    return render_template('signIn.html')



if __name__ == '__main__':
    app.run(debug=True)
