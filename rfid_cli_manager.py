import RPi.GPIO as GPIO
import mysql.connector
import time
from mfrc522 import SimpleMFRC522

# Define the GPIO pin for the buzzer
BUZZER_PIN = 18  # Change if needed

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize RFID reader
reader = SimpleMFRC522()

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host="smarthome.local",
        user="admin",
        password="Password123",
        database="rfid_access"
    )

def beep(times=1, duration=0.1):
    """Make the buzzer beep."""
    for _ in range(times):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(duration)

def scan_rfid():
    """Scan an RFID tag and return the UID."""
    print("Scan an RFID tag...")
    uid, _ = reader.read()
    print(f"Scanned UID: {uid}")
    beep(2)
    return str(uid)

def view_users():
    """Fetch and display users from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, rfid_uid, name, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    
    print("\n=== Registered Users ===")
    print("ID | RFID UID       | Name           | Created At")
    print("--------------------------------------------------")
    for user in users:
        print(f"{user[0]} | {user[1]} | {user[2]} | {user[3]}")
    beep(2)

def add_user():
    """Add a new RFID user by scanning a tag."""
    rfid_uid = scan_rfid()
    name = input("Enter User Name: ")
    
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (rfid_uid, name) VALUES (%s, %s)", (rfid_uid, name))
        conn.commit()
        print("User added successfully!")
        beep(3)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    conn.close()

def delete_user():
    """Delete a user by scanning an RFID tag."""
    rfid_uid = scan_rfid()
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE rfid_uid = %s", (rfid_uid,))
    conn.commit()
    conn.close()
    print("User deleted successfully!")
    beep(1)

def view_logs():
    """Fetch and display access logs."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, rfid_uid, status, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()
    
    print("\n=== Access Logs (Last 10 Entries) ===")
    print("ID | RFID UID       | Status  | Timestamp")
    print("--------------------------------------------------")
    for log in logs:
        print(f"{log[0]} | {log[1]} | {log[2]} | {log[3]}")
    beep(2)

def main_menu():
    """Display the main menu for managing the RFID system."""
    while True:
        print("\n============================")
        print("   RFID Access Management  ")
        print("============================")
        print("1. View Users")
        print("2. Add User (Scan RFID Tag)")
        print("3. Delete User (Scan RFID Tag)")
        print("4. View Access Logs")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            view_users()
        elif choice == "2":
            add_user()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            view_logs()
        elif choice == "5":
            print("Exiting...")
            beep(1)
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    try:
        main_menu()
    finally:
        GPIO.cleanup()
