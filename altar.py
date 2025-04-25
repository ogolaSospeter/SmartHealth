import sqlite3

def update_status_in_enrollments():
    try:
        conn = sqlite3.connect('smarthealthdatabase.db')
        cursor = conn.cursor()

        # Step 1: Update the status in 'program_enrollments' based on 'health_programs' status
        cursor.execute('''
        UPDATE program_enrollments
        SET status = (
            SELECT status
            FROM health_programs
            WHERE health_programs.id = program_enrollments.program_id
        );
        ''')

        # Step 2: Create a trigger to automatically set the status when a new enrollment is inserted
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_status_after_insert
        AFTER INSERT ON program_enrollments
        BEGIN
            UPDATE program_enrollments
            SET status = (
                SELECT status
                FROM health_programs
                WHERE health_programs.id = NEW.program_id
            )
            WHERE id = NEW.id;
        END;
        ''')

        # Commit the changes
        conn.commit()
        conn.close()

        print("Database updated successfully with the correct program statuses.")

    except sqlite3.Error as e:
        print(f"An error occurred while updating the database: {e}")

if __name__ == '__main__':
    update_status_in_enrollments()
