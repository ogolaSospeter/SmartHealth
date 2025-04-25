import sqlite3

def init_db():
    try:
        conn = sqlite3.connect('smarthealthdatabase.db')
        cursor = conn.cursor()

        cursor.executescript('''
        -- Doctors table
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_number TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            specialty TEXT NOT NULL,
            address TEXT NOT NULL,
            year_of_experience INTEGER NOT NULL,
                             city TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Health Programs table
        CREATE TABLE IF NOT EXISTS health_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            program_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            target_group TEXT NOT NULL,
            estimated_clients INTEGER NOT NULL,
            require_referral BOOLEAN DEFAULT 0,
            follow_up BOOLEAN DEFAULT 0,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES doctors(id)
        );

        -- Milestones table
        CREATE TABLE IF NOT EXISTS program_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER,
            title TEXT NOT NULL,
            target_date DATE NOT NULL,
            description TEXT,
            FOREIGN KEY (program_id) REFERENCES health_programs(id)
        );

        -- Resources table
        CREATE TABLE IF NOT EXISTS program_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER,
            resource_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (program_id) REFERENCES health_programs(id)
        );


        -- Clients table
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            gender TEXT NOT NULL,
            contact_number TEXT,
            email TEXT UNIQUE,
                             national_id TEXT UNIQUE,
            address TEXT
        );

        -- Program Enrollments table
        CREATE TABLE IF NOT EXISTS program_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            program_id INTEGER NOT NULL,
            enrolled_by INTEGER NOT NULL,
            enrollment_date DATE NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (client_id) REFERENCES clients(national_id),
            FOREIGN KEY (program_id) REFERENCES health_programs(id),
            FOREIGN KEY (enrolled_by) REFERENCES doctors(id),
            UNIQUE (client_id, program_id)
        );
        ''')

        conn.commit()
        conn.close()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")


if __name__ == '__main__':
    init_db()
