import json
import os
from datetime import datetime
import pytz

DB_FILE = 'db.json'

# Initialize DB if it doesn't exist
def init_db():
    if not os.path.exists(DB_FILE):
        default_data = {
            "system_status": "Closed",
            "students": [],
            "staff": [
                # DEFAULT SECURITY ACCOUNT TO UNLOCK SYSTEM
                {
                    "id": "SEC001",
                    "name": "Head of Security",
                    "email": "security01@unizulu.ac.za",
                    "year_employed": "2023"
                }
            ],
            "attendance_logs": [],
            "security_logs": []
        }
        with open(DB_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)

def load_data():
    if not os.path.exists(DB_FILE):
        init_db()
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Validation Functions ---
def validate_student(student_id, email):
    if not (student_id.isdigit() and len(student_id) == 9):
        return False, "Student ID must be exactly 9 digits."
    expected_email = f"{student_id}@unizulu.ac.za"
    if email != expected_email:
        return False, f"Student email must be in format: {expected_email}"
    return True, "Valid"

def validate_staff(email):
    if "@unizulu.ac.za" not in email:
        return False, "Staff email must contain '@unizulu.ac.za'"
    return True, "Valid"

# --- User Management ---
def add_user(role, data):
    db = load_data()
    if role == 'student':
        if any(u['id'] == data['id'] for u in db['students']):
            return False, "Student ID already exists."
        db['students'].append(data)
    elif role == 'staff':
        if any(u['id'] == data['id'] for u in db['staff']):
            return False, "Staff ID already exists."
        db['staff'].append(data)
    save_data(db)
    return True, "User added successfully."

# Define SA timezone
SA_TIMEZONE = pytz.timezone('Africa/Johannesburg')

# --- Logging Functions ---
def log_attendance(student_id, venue, reason):
    db = load_data()

     # Get current time in SA timezone first
    now = datetime.now(SA_TIMEZONE)
    
    entry = {
        "student_id": student_id,
        "time": now().strftime("%H:%M:%S"),
        "date": now().strftime("%Y-%m-%d"),
        "venue": venue,
        "reason": reason
    }
    db['attendance_logs'].append(entry)
    save_data(db)

def log_security_login(staff_id):
    db = load_data()

    # Get current time in SA timezone
    now = datetime.now(SA_TIMEZONE)
    
    entry = {
        "staff_id": staff_id,
        "login_time": now().strftime("%H:%M:%S"),
        "date": now().strftime("%Y-%m-%d")
    }
    db['security_logs'].append(entry)
    save_data(db)

def log_security_shift(staff_id, venue):
    db = load_data()
    staff_info = next((s for s in db['staff'] if s['id'] == staff_id), None)
    if not staff_info:
        return False, "Staff ID not found in database."

    # Get current time in SA timezone
    now = datetime.now(SA_TIMEZONE)
    
    entry = {
        "staff_id": staff_id,
        "staff_name": staff_info['name'],
        "venue": venue,
        "time": now().strftime("%H:%M:%S"),
        "date": now().strftime("%Y-%m-%d"),
        "action": "Shift Start"
    }
    db['security_logs'].append(entry)
    save_data(db)
    return True, "Shift logged successfully."

# --- System State Management ---
def get_system_state():
    db = load_data()
    return db.get('system_status', 'Closed')

def set_system_state(state, staff_id):
    db = load_data()
    db['system_status'] = state
    db['last_changed_by'] = staff_id
    save_data(db)
