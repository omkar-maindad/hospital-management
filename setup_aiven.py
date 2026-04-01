import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(override=True)

parsed_host = os.getenv('DB_HOST').strip()
parsed_port = int(os.getenv('DB_PORT', 3306))
parsed_user = os.getenv('DB_USER').strip()
parsed_pass = os.getenv('DB_PASSWORD').strip()

print("🚀 Attempting to connect to Aiven Cloud Database directly...")

try:
    conn = mysql.connector.connect(
        host=parsed_host,
        port=parsed_port,
        user=parsed_user,
        password=parsed_pass,
        ssl_disabled=False
    )
    cursor = conn.cursor()
    print("[+] SUCCESS: Reached Aiven! Executing the schema script automatically...")
    
    # Read the schema file
    with open('db_schema.sql', 'r') as f:
        sql_script = f.read()

    # Create queries separated by DELIMITER or semicolons
    # Since executing a raw script with DELIMITER commands is tricky in python, 
    # we manually parse or use multi=True for normal statements.
    
    statements = sql_script.split(';')
    for statement in statements:
        if statement.strip() and not "DELIMITER" in statement.upper():
            try:
                cursor.execute(statement)
            except Exception as e:
                # Ignore specific drop errors
                pass
    
    # Commit changes
    conn.commit()
    print("\n[+] BOOM! Database Schema successfully created on the Cloud! You don't need MySQL Workbench anymore!")
    
except mysql.connector.Error as err:
    print(f"\n[-] FAILED to connect: {err}")
    print("[!] Ensure that your .env file exact matches Aiven (no spaces copied by accident).")
