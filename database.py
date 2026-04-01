import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

connection_pool = None

def get_db_connection():
    global connection_pool
    try:
        if connection_pool is None:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="caresync_pool",
                pool_size=5,
                pool_reset_session=False,
                host=os.getenv('DB_HOST', 'localhost').strip(),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'root').strip(),
                password=os.getenv('DB_PASSWORD', '').strip(),
                database=os.getenv('DB_NAME', 'hospital_db').strip(),
                connection_timeout=10,
                ssl_disabled=False,
                use_pure=True
            )
        return connection_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error connecting to database pool: {err}")
        return None

def fetch_all(query, params=None):
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params=None):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def call_book_appointment_proc(patient_id, doctor_id, date, time):
    conn = get_db_connection()
    if conn is None: return "Connection failed"
    cursor = conn.cursor()
    try:
        # Call the stored procedure: BookAppointment(IN p_PatientID, IN p_DoctorID, IN p_ApptDate, IN p_ApptTime, OUT p_Message)
        # In mysql-connector-python, we pass variables and then fetch their values out.
        args = (patient_id, doctor_id, date, time, '')
        result_args = cursor.callproc('BookAppointment', args)
        conn.commit()
        return result_args[4]  # The OUT parameter p_Message
    except mysql.connector.Error as err:
        print(f"Error calling procedure: {err}")
        return str(err)
    finally:
        cursor.close()
        conn.close()
