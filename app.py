import streamlit as st
import pandas as pd
from datetime import datetime

# Page settings
st.set_page_config(
    page_title="Attendance & Engagement Agent",
    page_icon="🎓",
    layout="wide"
)

# App title
st.title("🎓 Multimodal Attendance & Engagement Agent")
st.write("Manage attendance and explore student engagement.")

# Store attendance data during the session
if "attendance" not in st.session_state:
    st.session_state.attendance = []

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Choose a page",
    ["Dashboard", "Mark Attendance", "Attendance Records"]
)

if page == "Dashboard":
    st.subheader("📊 Dashboard")

    records = pd.DataFrame(st.session_state.attendance)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Attendance Records", len(records))

    with col2:
        total_students = (
            records["Student Name"].nunique()
            if not records.empty else 0
        )
        st.metric("Students Recorded", total_students)

    with col3:
        st.metric("System Status", "Running")

    st.info(
        "This is the initial dashboard. "
        "Camera-based analysis, audio analysis and AI insights "
        "will be added in later development stages."
    )

elif page == "Mark Attendance":
    st.subheader("📝 Mark Attendance")

    with st.form("attendance_form"):
        student_name = st.text_input("Student Name")
        status = st.selectbox(
            "Attendance Status",
            ["Present", "Absent", "Late"]
        )

        submitted = st.form_submit_button("Save Attendance")

    if submitted:
        if student_name.strip():
            st.session_state.attendance.append({
                "Student Name": student_name.strip(),
                "Status": status,
                "Date & Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })
            st.success(f"Attendance saved for {student_name.strip()}!")
        else:
            st.warning("Please enter a student name.")

elif page == "Attendance Records":
    st.subheader("📋 Attendance Records")

    records = pd.DataFrame(st.session_state.attendance)

    if records.empty:
        st.info("No attendance records yet. Add one from Mark Attendance.")
    else:
        st.dataframe(records, use_container_width=True)

        csv_data = records.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Records as CSV",
            data=csv_data,
            file_name="attendance_records.csv",
            mime="text/csv"
        )
