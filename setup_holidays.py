import database as db

query = """
CREATE TABLE IF NOT EXISTS HospitalHolidays (
    HolidayID INT AUTO_INCREMENT PRIMARY KEY,
    HolidayDate DATE NOT NULL,
    Description VARCHAR(255) DEFAULT 'Public Holiday',
    UNIQUE KEY unique_holiday (HolidayDate)
);
"""
if db.execute_query(query):
    print("Table HospitalHolidays successfully built.")
else:
    print("Creation Failure.")
