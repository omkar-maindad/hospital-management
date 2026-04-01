import database

conn = database.get_db_connection()
if conn:
    print("\n[+] SUCCESS: Connected to the database successfully!")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM Patients;")
        patients_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Doctors;")
        doctors_count = cursor.fetchone()[0]
        print(f"[i] Found {patients_count} Patients and {doctors_count} Doctors inside hospital_db.")
        
        if patients_count == 0:
            print("[-] CAUSE: The connection works, but the tables are empty! You need to re-run db_schema.sql in Workbench to insert the mock data.")
    except Exception as e:
        print(f"[-] CAUSE: Query failed. {str(e)}")
else:
    print("\n[-] FAILED: Could not connect to the database. The root password in .env is still incorrect or MySQL is not running on port 3306.")
