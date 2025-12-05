import streamlit as st
import sqlite3
import uuid
import hashlib

# --------------------------
# DATABASE SETUP
# --------------------------
conn = sqlite3.connect('doctor_app.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    username TEXT UNIQUE,
    password TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    symptoms TEXT,
    doctor_id INTEGER,
    query_id TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id TEXT,
    reply TEXT
)''')
conn.commit()

# --------------------------
# HELPER FUNCTIONS
# --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def doctor_login(username, password):
    cursor.execute("SELECT * FROM doctors WHERE username=? AND password=?", (username, hash_password(password)))
    return cursor.fetchone()

# --------------------------
# STREAMLIT UI
# --------------------------
st.set_page_config(page_title="Doctor Consultation App", layout="wide")
st.title("🩺 Doctor Consultation System (Upgraded)")

menu = st.sidebar.radio("Select Role", ["Patient", "Doctor Login", "Doctor Registration"])

# --------------------------
# DOCTOR REGISTRATION
# --------------------------
if menu == "Doctor Registration":
    st.header("🧑‍⚕️ Doctor Registration")

    dname = st.text_input("Doctor Name")
    dphone = st.text_input("Phone Number")
    dun = st.text_input("Create Username")
    dpw = st.text_input("Create Password", type="password")

    if st.button("Register Doctor"):
        if dname and dphone and dun and dpw:
            try:
                cursor.execute("INSERT INTO doctors(name, phone, username, password) VALUES (?,?,?,?)",
                               (dname, dphone, dun, hash_password(dpw)))
                conn.commit()
                st.success("Doctor Registered Successfully!")
            except:
                st.error("Username already exists!")
        else:
            st.error("Fill all fields!")

# --------------------------
# DOCTOR LOGIN
# --------------------------
if menu == "Doctor Login":
    st.header("🧑‍⚕️ Doctor Login")

    un = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        doc = doctor_login(un, pw)
        if doc:
            st.success(f"Welcome Dr. {doc[1]}")
            st.subheader("📋 Patient Queries")

            cursor.execute("SELECT * FROM patients WHERE doctor_id=?", (doc[0],))
            all_patients = cursor.fetchall()

            for p in all_patients:
                st.write("---")
                st.write(f"👤 **{p[1]}** ({p[2]} years)")
                st.write(f"📝 Symptoms: {p[3]}")

                reply_text = st.text_area(f"Reply to {p[1]}", key=p[5])

                if st.button(f"Send Reply for {p[1]}"):
                    cursor.execute("INSERT INTO replies(query_id, reply) VALUES (?,?)", (p[5], reply_text))
                    conn.commit()
                    st.success("Reply Sent!")
        else:
            st.error("Invalid login!")

# --------------------------
# PATIENT SECTION
# --------------------------
if menu == "Patient":
    st.header("👤 Patient Consultation")

    # Show doctor list
    cursor.execute("SELECT id, name, phone FROM doctors")
    docs = cursor.fetchall()

    doctor_list = {f"Dr. {d[1]} (📞 {d[2]})": d[0] for d in docs}

    name = st.text_input("Your Name")
    age = st.number_input("Your Age", 1, 120)
    symptoms = st.text_area("Describe your symptoms")
    selected_doctor = st.selectbox("Choose Doctor", list(doctor_list.keys()))

    if st.button("Submit Query"):
        qid = str(uuid.uuid4())
        cursor.execute("INSERT INTO patients(name, age, symptoms, doctor_id, query_id) VALUES (?,?,?,?,?)",
                       (name, age, symptoms, doctor_list[selected_doctor], qid))
        conn.commit()
        st.success("Your query has been sent to the doctor!")

    # Show replies
    st.subheader("📨 Doctor Replies")
    cursor.execute("SELECT * FROM patients WHERE name=?", (name,))
    my_qs = cursor.fetchall()

    for q in my_qs:
        cursor.execute("SELECT reply FROM replies WHERE query_id=?", (q[5],))
        r = cursor.fetchone()
        if r:
            st.write("---")
            st.success(f"Doctor Reply: {r[0]}")
