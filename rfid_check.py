import RPi.GPIO as GPIO
import mysql.connector
import time
from mfrc522 import SimpleMFRC522

# Database connection details
DB_HOST = "smarthome.local"
DB_USER = "admin"       # Change to your database user
DB_PASSWORD = "Password123"  # Change to your database password
DB_NAME = "rfid_access"

# Initialize RFID reader
reader = SimpleMFRC522()

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def log_access(rfid_uid, status, user_name=None):
    """Log RFID access attempts in both the database and a text file."""
    conn = connect_db()
    cursor = conn.cursor()

    # Log to MySQL database
    cursor.execute("INSERT INTO access_logs (rfid_uid, status) VALUES (%s, %s)", (rfid_uid, status))
    conn.commit()
    cursor.close()
    conn.close()

    # Log to local file
    with open("rfid_log.txt", "a") as log_file:
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - UID: {rfid_uid} - Status: {status}"
        if user_name:
            log_entry += f" - User: {user_name}"
        log_file.write(log_entry + "\n")

def check_rfid(uid):
    """Check if the RFID tag is in the database and return the user name."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Query database
        cursor.execute("SELECT name FROM users WHERE rfid_uid = %s", (str(uid),))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return user name
        else:
            return None  # User not found

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

try:
    print("Scan an RFID tag...")

    while True:
        # Read RFID tag
        uid, _ = reader.read()
        print(f"RFID UID: {uid}")

        # Check the tag in the database
        user_name = check_rfid(uid)

        if user_name:
            print(f"✅ Access Granted: Welcome, {user_name}!")
            log_access(uid, "GRANTED", user_name)
        else:
            print("❌ Access Denied: Unknown RFID tag.")
            log_access(uid, "DENIED")

        print("\nScan another tag or press Ctrl+C to exit.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
