import json
import os

DB_FILE = 'db.json'

def reset_database():
    #Create the structure with correct keys
    data = {
        "system_status": "Closed",
        "students": [],
        "staff": [
            {"id": "SEC001", "name": "Security", "email": "security01@unizulu.ac.za", "year_employed": "2018"}
        ],
        "attendance_logs": [],
        "security_logs": []
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
        print("Database reset successful!")
        print("System Status: CLOSED")
        print("Default Staff ID created: SEC001")
        
        if __name__=="__main__":
            reset_database()