import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

# Configure the application
st.set_page_config(
    page_title="Attendance & Engagement Agent",
    page_icon="🎓",
    layout="wide"
)

# Define project file paths
BASE_DIR = Path(__file__).resolve().parent
ATTENDANCE_FILE = BASE_DIR / "attendance.csv"

# Initialize manual attendance records
if "manual_attendance" not in st.session_state:
    st.session_state.manual_attendance = []

# Load face-based attendance records
def load_face_attendance():
    if ATTENDANCE_FILE.exists():
        try:
            return pd.read_csv(ATTENDANCE_FILE)
        except (pd.errors.ParserError, UnicodeDecodeError):
            st.error("The attendance CSV file could not be read.")
    return pd.DataFrame(
        columns=["face_id", "presence_seconds", "status"]
    )

# Display the application header
st.title("🎓 Multimodal Attendance & Engagement Agent")
st.caption(
    "Face tracking, attendance monitoring and engagement analytics"
)

# Create navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Mark Attendance",
        "Face Attendance",
        "Audio Analysis",
        "AI Insights",
        "Attendance Records"
    ]
)

# Load the latest face attendance data
face_records = load_face_attendance()
manual_records = pd.DataFrame(st.session_state.manual_attendance)

if page == "Dashboard":
    st.header("📊 Dashboard")

    total_faces = len(face_records)
    present_faces = (
        int((face_records["status"] == "Present").sum())
        if not face_records.empty else 0
    )
    manual_count = len(manual_records)

    col1, col2, col3 = st.columns(3)

    col1.metric("Tracked Face IDs", total_faces)
    col2.metric("Present", present_faces)
    col3.metric("Manual Records", manual_count)

    st.subheader("Latest Face Attendance")

    if face_records.empty:
        st.info(
            "No face attendance data found. "
            "Run face_tracking.py and attendance.py on your computer first."
        )
    else:
        st.dataframe(face_records, use_container_width=True)

    st.caption(
        "Face IDs are temporary tracking labels, not verified identities."
    )

elif page == "Mark Attendance":
    st.header("📝 Mark Manual Attendance")

    with st.form("attendance_form"):
        student_name = st.text_input("Student Name")
        status = st.selectbox(
            "Attendance Status",
            ["Present", "Absent", "Late"]
        )
        submitted = st.form_submit_button("Save Attendance")

    if submitted:
        if student_name.strip():
            st.session_state.manual_attendance.append({
                "Student Name": student_name.strip(),
                "Status": status,
                "Date & Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })
            st.success(
                f"Attendance saved for {student_name.strip()}!"
            )
        else:
            st.warning("Please enter a student name.")

elif page == "Face Attendance":
    st.header("📷 Face-Based Attendance")

    if face_records.empty:
        st.warning(
            "No attendance results found. "
            "Run the local tracking and attendance scripts first."
        )
    else:
        col1, col2 = st.columns(2)

        present_count = int(
            (face_records["status"] == "Present").sum()
        )
        absent_count = int(
            (face_records["status"] == "Absent").sum()
        )

        col1.metric("Present Face IDs", present_count)
        col2.metric("Absent Face IDs", absent_count)

        st.dataframe(face_records, use_container_width=True)

        st.download_button(
            "Download Face Attendance CSV",
            data=face_records.to_csv(index=False).encode("utf-8"),
            file_name="attendance.csv",
            mime="text/csv"
        )

    if st.button("Refresh Attendance"):
        st.rerun()

elif page == "Attendance Records":
    st.header("📋 Attendance Records")

    st.subheader("Manual Attendance")

    if manual_records.empty:
        st.info("No manual attendance records have been added.")
    else:
        st.dataframe(manual_records, use_container_width=True)

        st.download_button(
            "Download Manual Records",
            data=manual_records.to_csv(index=False).encode("utf-8"),
            file_name="manual_attendance.csv",
            mime="text/csv"
        )

    st.subheader("Face Attendance")

    if face_records.empty:
        st.info("No face attendance records are available.")
    else:
        st.dataframe(face_records, use_container_width=True)

elif page == "Audio Analysis":
    st.header("🎙️ Audio Analysis")

    audio_file = BASE_DIR / "audio_analysis.csv"
    summary_file = BASE_DIR / "session_audio_summary.csv"

    if audio_file.exists():
        audio_df = pd.read_csv(audio_file)
        st.subheader("Segment-Level Results")
        st.dataframe(audio_df, use_container_width=True)
    else:
        st.info("Run audio_analysis.py to generate audio results.")

    if summary_file.exists():
        summary_df = pd.read_csv(summary_file)
        st.subheader("Session Summary")
        st.dataframe(summary_df, use_container_width=True)

        st.download_button(
            "Download Audio Analysis CSV",
            data=audio_df.to_csv(index=False).encode("utf-8")
            if audio_file.exists() else summary_df.to_csv(index=False).encode("utf-8"),
            file_name="audio_analysis.csv",
            mime="text/csv"
        )  


elif page == "AI Insights":
    st.header("🤖 Multimodal AI Insights")

    # Load AI insights
    insights_file = BASE_DIR / "engagement_insights.csv"

    if insights_file.exists():
        insights = pd.read_csv(insights_file)

        if not insights.empty:
            st.subheader("Engagement Insights")
            st.dataframe(insights, use_container_width=True)

            st.download_button(
                "Download AI Insights",
                data=insights.to_csv(index=False).encode("utf-8"),
                file_name="engagement_insights.csv",
                mime="text/csv"
            )
        else:
            st.info("The insights file is empty.")
    else:
        st.warning(
            "Run multimodal_agent.py first to generate AI insights."
        )

    # Display multimodal fusion results
    st.subheader("Multimodal Signal Fusion")

    fusion_file = BASE_DIR / "multimodal_fusion.csv"

    if fusion_file.exists():
        fusion_data = pd.read_csv(fusion_file)

        if not fusion_data.empty:
            st.dataframe(fusion_data, use_container_width=True)

            st.download_button(
                "Download Fusion Results",
                data=fusion_data.to_csv(index=False).encode("utf-8"),
                file_name="multimodal_fusion.csv",
                mime="text/csv"
            )
        else:
            st.info("The fusion file is empty.")
    else:
        st.info(
            "Run multimodal_fusion.py to generate fusion results."
        )

    # Display engagement scores
    st.subheader("📊 Engagement Scores")

    scores_file = BASE_DIR / "engagement_scores.csv"

    if scores_file.exists():
        scores_df = pd.read_csv(scores_file)

        if not scores_df.empty:
            st.dataframe(scores_df, use_container_width=True)

            # Display the latest available score
            if "engagement_score" in scores_df.columns:
                latest_score = scores_df["engagement_score"].iloc[-1]
                st.metric(
                    "Prototype Engagement Score",
                    f"{latest_score:.1f}/100"
                )

            if "engagement_level" in scores_df.columns:
                latest_level = scores_df["engagement_level"].iloc[-1]
                st.write(f"**Rule-based level:** {latest_level}")

            st.download_button(
                "Download Engagement Scores",
                data=scores_df.to_csv(index=False).encode("utf-8"),
                file_name="engagement_scores.csv",
                mime="text/csv"
            )

            st.caption(
                "Prototype score based on available signals only. "
                "It does not verify attention, speech, or learning."
            )
        else:
            st.info("The engagement scores file is empty.")
    else:
        st.warning(
            "Run engagement_score.py first to generate engagement scores."
        )

    # Display instructor-facing teaching suggestions
    st.subheader("👨‍🏫 Teaching Suggestions")

    suggestions_file = BASE_DIR / "teaching_suggestions.csv"

    if suggestions_file.exists():
        suggestions_df = pd.read_csv(suggestions_file)

        if not suggestions_df.empty:
            st.dataframe(
                suggestions_df,
                use_container_width=True
            )

            st.download_button(
                "Download Teaching Suggestions",
                data=suggestions_df.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="teaching_suggestions.csv",
                mime="text/csv"
            )

            st.caption(
                "These are optional, rule-based teaching suggestions "
                "derived from available signals. They do not confirm "
                "student attention or classroom behavior."
            )
        else:
            st.info("No teaching suggestions are available yet.")
    else:
        st.warning(
            "Run teaching_suggestions.py first to generate suggestions."
        )

        
    # Student-Facing Analytics
    st.subheader("Student-Facing Analytics")

    student_analytics_file = BASE_DIR / "student_analytics.csv"

    if student_analytics_file.exists():
        student_df = pd.read_csv(student_analytics_file)

        if not student_df.empty:
            st.dataframe(student_df, use_container_width=True)

            st.download_button(
                label="Download Student Analytics",
                data=student_df.to_csv(index=False).encode("utf-8"),
                file_name="student_analytics.csv",
                mime="text/csv"
            )

            st.caption(
                "This report supports student reflection. "
                "Prototype scores do not measure actual attention, "
                "learning, or academic performance."
            )
        else:
            st.info("Student analytics file is empty.")
    else:
        st.warning(
            "Run student_analytics.py to generate student analytics."
        )
