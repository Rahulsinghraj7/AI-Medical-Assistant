import streamlit as st
from streamlit_option_menu import option_menu
import ollama
from datetime import datetime
import sqlite3

# PAGE CONFIG
st.set_page_config(
    page_title="AI Hospital System Pro",
    page_icon="🩺",
    layout="wide"
)
# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #F4F9FF;
}

/* Main Title */
.main-title {
    font-size: 45px;
    color: #0077B6;
    text-align: center;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-title {
    text-align: center;
    font-size: 20px;
    color: #555;
    margin-bottom: 30px;
}

.feature-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    text-align: center;
    margin: 10px;
    color: #1E293B;
}

/* Card Heading */
.feature-card h3 {
    color: #0077B6;
}

/* Card Paragraph */
.feature-card p {
    color: #333333;
}

}

/* Buttons */
.stButton button {
    background-color: #0077B6;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

/* Button Hover */
.stButton button:hover {
    background-color: #023E8A;
    color: white;
}

/* Input Boxes */
.stTextInput input {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "chat" not in st.session_state:
    st.session_state.chat = []
if "reports" not in st.session_state:
    st.session_state.reports = []
if "patient" not in st.session_state:
    st.session_state.patient = None
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

# DATABASE INIT
conn = sqlite3.connect("hospital_ai.db", check_same_thread=False)
cursor = conn.cursor()

# APPOINTMENT TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    patient_name TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT,
    reason TEXT
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT,
    city TEXT,
    mobile TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    name TEXT,
    time TEXT,
    report TEXT
)
""")
conn.commit()

# PATIENT ID
def generate_patient_id():
    return "AI-" + datetime.now().strftime("%Y%m%d-%H%M%S")

# MAIN CSS
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, #1e3a8a 0%, transparent 30%),
        radial-gradient(circle at bottom right, #0f766e 0%, transparent 30%),
        linear-gradient(135deg,#020617,#0f172a,#111827);
    background-attachment: fixed;
    color: white;
}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.75);
    backdrop-filter: blur(18px);
}
.stButton > button {
    width:100%;
    height:55px;
    border:none;
    border-radius:16px;
    font-size:18px;
    font-weight:bold;
    color:white;
    background:linear-gradient(90deg,#06b6d4,#3b82f6);
    transition:0.3s;
    box-shadow:0 5px 20px rgba(59,130,246,0.4);
}
.stButton > button:hover {
    transform:translateY(-3px);
    box-shadow:0 0 35px rgba(59,130,246,0.7);
}
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: rgba(255,255,255,0.95) !important;
    color: black !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
/* SELECTBOX */
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.95) !important;
    color: black !important;
    border-radius: 14px !important;
}
.user {
    text-align:right;
    background:linear-gradient(90deg,#2563eb,#3b82f6);
    padding:14px;
    border-radius:16px;
    margin:10px 0;
}
.ai {
    text-align:left;
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.08);
    padding:14px;
    border-radius:16px;
    margin:10px 0;
}
.report {
    background:rgba(255,255,255,0.08);
    padding:20px;
    border-radius:18px;
    margin:15px 0;
    border:1px solid rgba(255,255,255,0.08);
}
.hero-title{
    text-align:center;
    font-size:72px;
    font-weight:900;
    background: linear-gradient(90deg,#38bdf8,#06b6d4,#3b82f6);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-top:20px;
}
.hero-sub{
    text-align:center;
    color:#cbd5e1;
    font-size:22px;
    margin-bottom:50px;
}
.glass-card{
    background: rgba(255,255,255,0.08);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:25px;
    padding:35px;
    text-align:center;
    backdrop-filter: blur(15px);
    transition:0.4s;
    height:260px;
}
.glass-card:hover{
    transform: translateY(-12px) scale(1.03);
    box-shadow:0 0 30px rgba(56,189,248,0.5);
}
.card-icon{
    font-size:70px;
    margin-bottom:15px;
}
.card-title{
    font-size:28px;
    font-weight:bold;
}
.card-text{
    color:#cbd5e1;
    margin-top:10px;
}
.diagnosis-card{
    background: rgba(255,255,255,0.08);
    border-radius:24px;
    padding:30px;
    margin-top:20px;
    backdrop-filter: blur(18px);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
}
.diagnosis-header{
    font-size:28px;
    font-weight:bold;
    margin-bottom:20px;
    color:#38bdf8;
}
.diagnosis-section{
    padding:20px;
    border-radius:16px;
    background: rgba(255,255,255,0.05);
    line-height:1.8;
}
.specialist-tag{
    display:inline-block;
    padding:10px 18px;
    border-radius:14px;
    background: linear-gradient(90deg,#06b6d4,#3b82f6);
    color:white;
    font-weight:bold;
    margin-top:15px;
}
.low-risk{
    background:#16a34a;
    padding:10px 18px;
    border-radius:14px;
    display:inline-block;
    font-weight:bold;
    color:white;
    margin-top:10px;
}
.medium-risk{
    background:#eab308;
    padding:10px 18px;
    border-radius:14px;
    display:inline-block;
    font-weight:bold;
    color:black;
    margin-top:10px;
}
.high-risk{
    background:#dc2626;
    padding:10px 18px;
    border-radius:14px;
    display:inline-block;
    font-weight:bold;
    color:white;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    page = option_menu(
        "AI Medical Assistant",
        [
            "Login",
            "Home",
            "Patient Registration",
            "Appointment Booking",
            "Consultation",
            "Dashboard",
            "Patient History",
            "Reports",
            "About"
        ],
        icons=[
            "key",
            "house",
            "person",
            "calender-check",
            "chat",
            "bar-chart",
            "clock-history",
            "file-medical",
            "info-circle"
        ],
        default_index=1
    )

# LOGIN
if page == "Login":
    st.title("🔐 Doctor Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):

        if username == "admin" and password == "admin":
            st.session_state.auth = True
            st.session_state.user = "Doctor Admin"
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# HOME
elif page == "Home":
    st.title("Home")
    st.markdown("""
    <div class="hero-title">
        🩺 AI Hospital System Pro
    </div>
    <div class="hero-sub">
        Smart AI-Powered Healthcare & Hospital Management Platform
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero'>
        <h1>🏥 AI Hospital System Pro</h1>
        <p>Intelligent Healthcare Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # ==========================================
    # AI DIAGNOSIS CARD
    # ==========================================

    with col1:

        st.markdown("""
        <div class="feature-card">
            <h3>🩺 AI Diagnosis</h3>
            <p>Smart symptom analysis using AI.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Diagnosis"):
            st.success("Scroll down to begin AI consultation.")

    # ==========================================
    # REPORT CARD
    # ==========================================

    with col2:

        st.markdown("""
        <div class="feature-card">
            <h3>📄 Medical Reports</h3>
            <p>Generate downloadable health reports.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Reports"):
            st.info("Medical reports section is available below.")

    # ==========================================
    # EMERGENCY CARD
    # ==========================================

    with col3:

        st.markdown("""
        <div class="feature-card">
            <h3>🚨 Emergency Detection</h3>
            <p>Detect critical health conditions instantly.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Emergency Help"):
            st.error("If this is an emergency, contact a doctor immediately.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🤖</div>
            <div class="card-title">AI Diagnosis</div>
            <div class="card-text">
                Advanced AI-powered disease prediction and consultation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">📄</div>
            <div class="card-title">Smart Reports</div>
            <div class="card-text">
                Generate professional patient reports instantly.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🏥</div>
            <div class="card-title">Hospital System</div>
            <div class="card-text">
                Manage patients and analytics.
            </div>
        </div>
        """, unsafe_allow_html=True)

# PATIENT REGISTRATION
elif page == "Patient Registration":
    st.title("🧑‍⚕️ Patient Registration")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    city = st.text_input("City")
    mobile = st.text_input("Mobile Number")

    if st.button("Register Patient"):

        if name == "" or city == "" or mobile == "":
            st.warning("Please fill all fields")

        else:

            patient_id = generate_patient_id()

            st.session_state.patient = {
                "id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "city": city,
                "mobile": mobile
            }

            cursor.execute(
                "INSERT OR REPLACE INTO patients VALUES (?,?,?,?,?,?)",
                (patient_id, name, age, gender, city, mobile)
            )

            conn.commit()

            st.success("Patient Registered Successfully")
            st.info(f"Patient ID: {patient_id}")

    # APPOINTMENT BOOKING
elif page == "Appointment Booking":
    st.title("📅 Appointment Booking")
    st.write("TESTING PAGE")

    # CHECK PATIENT
    if not st.session_state.patient:
        st.warning("Please register patient first")
        st.stop()

    # PATIENT INFO
    st.info(
        f"Patient: {st.session_state.patient['name']} | "
        f"ID: {st.session_state.patient['id']}"
    )
    # DOCTOR SELECTION
    doctor = st.selectbox(
        "Select Doctor",
        [
            "Dr. P Garg - Cardiologist",
            "Dr. R Singh - Dermatologist",
            "Dr. K Singh - Neurologist",
            "Dr. Khan - General Physician",
            "Dr. Singh - Orthopedic"
        ]
    )

    # DATE
    appointment_date = st.date_input(
        "Appointment Date"
    )

    # TIME SLOT
    appointment_time = st.selectbox(
        "Select Time Slot",
        [
            "09:00 AM",
            "10:00 AM",
            "11:00 AM",
            "12:00 PM",
            "02:00 PM",
            "03:00 PM",
            "04:00 PM"
        ]
    )

    # REASON
    reason = st.text_area(
        "Reason for Visit",
        placeholder="Describe health issue..."
    )

    # BOOK BUTTON
    if st.button("Book Appointment"):
        cursor.execute(
            """
            INSERT INTO appointments
            (
                patient_id,
                patient_name,
                doctor,
                date,
                time,
                reason
            )
            VALUES (?,?,?,?,?,?)
            """,
            (
                st.session_state.patient["id"],
                st.session_state.patient["name"],
                doctor,
                str(appointment_date),
                appointment_time,
                reason
            )
        )

        conn.commit()

        st.success("✅ Appointment Booked Successfully")

        st.markdown(f"""
         <div class="report">

         <h3>📅 Appointment Confirmation</h3>

         <b>Patient:</b>
         {st.session_state.patient['name']}<br><br>

         <b>Doctor:</b>
         {doctor}<br><br>

         <b>Date:</b>
         {appointment_date}<br><br>

         <b>Time:</b>
         {appointment_time}<br><br>

         <b>Reason:</b>
         {reason}

         </div>
         """, unsafe_allow_html=True)

# CONSULTATION
elif page == "Consultation":
    st.title("💬 AI Consultation")
    if not st.session_state.patient:
        st.warning("Please register patient first")
        st.stop()

    st.info(
        f"Patient: {st.session_state.patient['name']} | "
        f"ID: {st.session_state.patient['id']}"
    )

    for c in st.session_state.chat:

        if c["role"] == "user":
            st.markdown(
                f"<div class='user'>👤 {c['msg']}</div>",
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                f"<div class='ai'>🧠 {c['msg']}</div>",
                unsafe_allow_html=True
            )

    st.markdown("## 👤 Patient Information")

    name = st.text_input("Patient Name")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        step=1
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    user_input = st.text_area(
        "Enter symptoms",
        placeholder="Example: fever, cough, headache"
    )

    danger_keywords = [
        "chest pain",
        "breathing problem",
        "blood vomiting",
        "unconscious",
        "heart attack",
        "severe bleeding"
    ]

    moderate_keywords = [
        "fever",
        "cough",
        "headache",
        "vomiting",
        "stomach pain"
    ]

    risk = "Low"

    for word in danger_keywords:
        if word in user_input.lower():
            risk = "High"

    for word in moderate_keywords:
        if word in user_input.lower() and risk != "High":
            risk = "Moderate"

    if user_input:

        if risk == "Low":
            st.markdown(
                '<div class="low-risk">🟢 Low Risk</div>',
                unsafe_allow_html=True
            )

        elif risk == "Moderate":
            st.markdown(
                '<div class="medium-risk">🟡 Moderate Risk</div>',
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                '<div class="high-risk">🔴 High Risk</div>',
                unsafe_allow_html=True
            )

            st.error("🚨 Seek immediate medical attention")

    if st.button("Send") and user_input.strip():

        st.session_state.chat.append({
            "role": "user",
            "msg": user_input
        })

        prompt = f"""
You are an advanced AI medical assistant.

Patient Information:
Name: {st.session_state.patient['name']}
Age: {st.session_state.patient['age']}
Gender: {st.session_state.patient['gender']}
City: {st.session_state.patient['city']}

Symptoms:
{user_input}

Provide response in this format:

## Possible Condition
## Severity Level
## Possible Causes
## Recommended Precautions
## Medicines or Care Suggestions
## Recommended Specialist Doctor
## Emergency Warning

Keep response professional and easy to understand.
"""

        try:

            with st.spinner("🧠 AI is analyzing patient symptoms..."):

                res = ollama.chat(
                    model="phi3:mini",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                reply = res["message"]["content"]

        except:
            reply = "⚠ Ollama not running"

        specialist = "General Physician"

        if "skin" in user_input.lower():
            specialist = "Dermatologist"

        elif "heart" in user_input.lower():
            specialist = "Cardiologist"

        elif "eye" in user_input.lower():
            specialist = "Ophthalmologist"

        elif "mental" in user_input.lower():
            specialist = "Psychiatrist"

        elif "bone" in user_input.lower():
            specialist = "Orthopedic"

        st.session_state.chat.append({
            "role": "ai",
            "msg": reply
        })

        st.markdown(f"""
        <div class="diagnosis-card">

            <div class="diagnosis-header">
                🧠 AI Diagnosis Report
            </div>

            <div class="diagnosis-section">
                {reply}
            </div>

            <div class="specialist-tag">
                👨‍⚕ Recommended Specialist: {specialist}
            </div>

        </div>
        """, unsafe_allow_html=True)

        cursor.execute(
            """
            INSERT INTO reports (patient_id, name, time, report)
            VALUES (?,?,?,?)
            """,
            (
                st.session_state.patient["id"],
                st.session_state.patient["name"],
                datetime.now().strftime("%H:%M"),
                reply
            )
        )

        conn.commit()

        st.session_state.reports.append({
            "id": st.session_state.patient["id"],
            "name": st.session_state.patient["name"],
            "age": st.session_state.patient["age"],
            "gender": st.session_state.patient["gender"],
            "city": st.session_state.patient["city"],
            "mobile": st.session_state.patient["mobile"],
            "time": datetime.now().strftime("%H:%M"),
            "report": reply
        })

        st.rerun()

# DASHBOARD
elif page == "Dashboard":
    st.title("📊 Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Chats", len(st.session_state.chat))
    with col2:
        st.metric("Reports", len(st.session_state.reports))
    with col3:
        cursor.execute("SELECT COUNT(*) FROM patients")
        st.metric("Patients", cursor.fetchone()[0])
    with col4:
        st.metric("AI Status", "Online ✅")
        with col5:
            cursor.execute("SELECT COUNT(*) FROM appointments")
            appointment_count = cursor.fetchone()[0]
            st.metric("Appointments", appointment_count)

# PATIENT HISTORY
elif page == "Patient History":
    st.title("🧾 Patient History")
    pid = st.text_input("Enter Patient ID")

    if st.button("Search"):

        cursor.execute(
            "SELECT * FROM patients WHERE id=?",
            (pid,)
        )

        patient = cursor.fetchone()

        if patient:

            st.success("Patient Found")

            st.write(f"Name: {patient[1]}")
            st.write(f"Age: {patient[2]}")
            st.write(f"Gender: {patient[3]}")
            st.write(f"City: {patient[4]}")
            st.write(f"Mobile: {patient[5]}")

            cursor.execute(
                "SELECT * FROM reports WHERE patient_id=?",
                (pid,)
            )

            reports = cursor.fetchall()

            for r in reversed(reports):

                st.markdown(f"""
                <div class="report">
                <b>Time:</b> {r[3]}<br><br>
                {r[4]}
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error("Patient not found")

# REPORTS
elif page == "Reports":
    st.title("📄 Patient Reports")
    # FETCH REPORTS FROM DATABASE
    cursor.execute("""
    SELECT patient_id, name, time, report
    FROM reports
    ORDER BY id DESC
    """)

    reports = cursor.fetchall()

    # NO REPORTS
    if not reports:
        st.warning("No reports found")

    else:

        for r in reports:

            st.markdown(f"""
            <div class="report">

            <h3>🧾 AI Medical Report</h3>

            <b>Patient ID:</b>
            {r[0]}<br><br>

            <b>Patient Name:</b>
            {r[1]}<br><br>

            <b>Time:</b>
            {r[2]}<br><br>

            <b>AI Diagnosis:</b><br>
            {r[3]}

            </div>
            """, unsafe_allow_html=True)

# ABOUT
elif page == "About":
    st.title("ℹ About")
    st.write("""
    AI Hospital System Pro is an advanced AI-powered
    healthcare and hospital management platform.

    Features:
    - AI Diagnosis
    - Risk Detection
    - Emergency Alerts
    - Specialist Recommendation
    - Patient Registration
    - Medical Reports
    - Dashboard Analytics
    """)

