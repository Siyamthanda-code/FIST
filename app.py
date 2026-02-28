import streamlit as st
import numpy as np
import cv2
import os
import joblib
from PIL import Image
import pandas as pd
import time
import db_manager
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="FIST - Fingerprint Identification Student Terminal", layout="wide")

# --- Helper Functions ---
@st.cache_resource
def load_model():
    try:
        return joblib.load('svm_fingerprint_model.pkl')
    except:
        return None

def preprocess_image(image_bytes):
    try:
        file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (312, 372))
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return img.flatten().reshape(1, -1)
    except Exception as e:
        return None

# --- SIDEBAR ---
logo_path = os.path.join('assets', 'logo.png')
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

st.sidebar.title("Navigation")
# IMPORTANT: Names must match the 'elif' logic below
page = st.sidebar.radio("Go to:", ["Dashboard", "Verify Attendance", "Security Portal", "User Management", "View Logs"])

# --- PAGE 1: DASHBOARD ---
if page == "Dashboard":
    st.title("📊 System Dashboard")
    db = db_manager.load_data()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(db['students']))
    with col2:
        st.metric("Security Personnel", len(db['staff']))
    with col3:
        st.metric("Attendance Logs", len(db['attendance_logs']))

    st.divider()
    st.subheader("🛡️ Security Personnel")
    if db['staff']:
        df_staff = pd.DataFrame(db['staff'])
        st.dataframe(df_staff, use_container_width=True, hide_index=True)
    else:
        st.info("No security personnel registered yet.")

# --- PAGE 2: VERIFY ATTENDANCE (FIXED INDENTATION) ---
elif page == "Verify Attendance":
    # Header
    col_text, col_img = st.columns([4, 1])
    with col_text:
        st.title("Fingerprint Verification")
    with col_img:
        fp_path = os.path.join('assets', 'fing.png')
        if os.path.exists(fp_path):
            st.image(fp_path, width=80)

    # CHECK SYSTEM STATE (Moved OUTSIDE of image logic)
    current_state = db_manager.get_system_state()
    
    if current_state == 'Closed':
        st.error("🔒 SYSTEM OFFLINE")
        st.warning("The system is currently locked. Security Personnel must open the system to allow attendance verification.")
        st.info("Please contact security or go to 'Security Portal' to open the system.")
    else:
        st.success("🔓 SYSTEM ONLINE")
        st.write("Upload a fingerprint scan to verify student identity and log attendance.")
        
        model = load_model()
        if model is None:
            st.error("Model not found. Train the model first.")
        else:
            col1, col2 = st.columns([2, 2])
            with col1:
                uploaded_file = st.file_uploader("Scan Fingerprint", type=['jpg', 'png', 'bmp'])
                venue = st.selectbox("Venue", ["King Bhekuzulu Hall", "D3/4", "HP 1", "HP 2", "HP 3", "Library", "NE 10", "NE 20", "B422-3 CHAPEL"])
                reason = st.selectbox("Reason", ["Lecture", "Exam", "Study", "Event"])
                
                if st.button("Verify & Log Attendance", type="primary"):
                    if uploaded_file:
                        with st.spinner("Processing..."):
                            uploaded_file.seek(0)
                            features = preprocess_image(uploaded_file)
                            if features is not None:
                                pred_id = model.predict(features)[0]
                                prob = model.predict_proba(features).max()
                                st.write(f"Debug Info - Confidence: {prob*100:.2f}%")
                                
                                if prob > 0.10:
                                    db_manager.log_attendance(pred_id, venue, reason)
                                    db = db_manager.load_data()
                                    student_info = next((s for s in db['students'] if s['id'] == pred_id), None)
                                    name = student_info['name'] if student_info else "Unknown"
                                    st.success(f"✅ ACCESS GRANTED")
                                    st.write(f"**Student:** {name} ({pred_id})")
                                else:
                                    st.error(f"❌ ACCESS DENIED: Confidence too low ({prob*100:.2f}%).")
                    else:
                        st.warning("Please upload a scan.")

# --- PAGE: SECURITY PORTAL (Name matches Navigation) ---
elif page == "Security Portal":
    st.title("🛡️ Security Personnel Portal")
    
    current_state = db_manager.get_system_state()
    if current_state == 'Open':
        st.success(f"Current System Status: **OPEN** (Accessible)")
    else:
        st.error(f"Current System Status: **CLOSED** (Locked)")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("System Control")
        st.write("Security staff can open or close the system.")
        staff_id_control = st.text_input("Enter Staff ID to Authorize", key="auth_id")
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("🔓 Open System", type="primary"):
                if staff_id_control:
                    db = db_manager.load_data()
                    if any(s['id'] == staff_id_control for s in db['staff']):
                        db_manager.set_system_state('Open', staff_id_control)
                        st.rerun()
                    else:
                        st.error("Invalid Staff ID.")
                else:
                    st.warning("Please enter Staff ID.")

        with btn_col2:
            if st.button("🔒 Close System"):
                if staff_id_control:
                    db = db_manager.load_data()
                    if any(s['id'] == staff_id_control for s in db['staff']):
                        db_manager.set_system_state('Closed', staff_id_control)
                        st.rerun()
                    else:
                        st.error("Invalid Staff ID.")
                else:
                    st.warning("Please enter Staff ID.")

    with col2:
        st.subheader("Shift Logging")
        with st.form("shift_form"):
            s_id = st.text_input("Staff ID")
            venue = st.selectbox("Assigned Venue", ["Main Hall", "Block A", "Computer Lab", "Library", "HP Lab", "D Block", "Chapel"])
            if st.form_submit_button("Log Shift Start"):
                if s_id:
                    success, msg = db_manager.log_security_shift(s_id, venue)
                    if success:
                        st.success(f"Shift Logged at {venue}")
                    else:
                        st.error(msg)
                else:
                    st.error("Enter Staff ID.")

# --- PAGE 3: USER MANAGEMENT ---
elif page == "User Management":
    tab1, tab2 = st.tabs(["Register Student", "Register Staff"])
    with tab1:
        st.subheader("Register New Student")
        with st.form("student_form"):
            s_id = st.text_input("Student Number (9 digits)")
            s_name = st.text_input("Full Name")
            s_email = st.text_input("Student Email")
            s_year = st.text_input("Year Registered")
            if st.form_submit_button("Add Student"):
                valid, msg = db_manager.validate_student(s_id, s_email)
                if valid:
                    data = {"id": s_id, "name": s_name, "email": s_email, "year_registered": s_year}
                    db_manager.add_user('student', data)
                    st.success(f"Student {s_name} registered!")
                else:
                    st.error(msg)

    with tab2:
        st.subheader("Register Security Staff")
        with st.form("staff_form"):
            st_id = st.text_input("Staff ID")
            st_name = st.text_input("Full Name")
            st_email = st.text_input("Staff Email (@unizulu.ac.za)")
            st_year = st.text_input("Year Employed")
            if st.form_submit_button("Add Staff"):
                valid, msg = db_manager.validate_staff(st_email)
                if valid:
                    data = {"id": st_id, "name": st_name, "email": st_email, "year_employed": st_year}
                    db_manager.add_user('staff', data)
                    st.success(f"Staff {st_name} added!")
                else:
                    st.error(msg)

# --- PAGE 4: VIEW LOGS ---
elif page == "View Logs":
    st.title("📜 Attendance & Security Logs")
    db = db_manager.load_data()
    tab1, tab2 = st.tabs(["Student Attendance", "Security Login Tracker"])
    with tab1:
        if db['attendance_logs']:
            st.dataframe(pd.DataFrame(db['attendance_logs']), use_container_width=True)
        else:
            st.info("No attendance recorded yet.")
    with tab2:
        if db['security_logs']:
            st.dataframe(pd.DataFrame(db['security_logs']), use_container_width=True)
        else:
            st.info("No security logs yet.")