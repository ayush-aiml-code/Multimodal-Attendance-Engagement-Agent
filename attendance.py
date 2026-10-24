
import os
import pandas as pd

# Project folder ka path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input aur output files
input_file = os.path.join(BASE_DIR, "tracking_log.csv")
output_file = os.path.join(BASE_DIR, "attendance.csv")

# Minimum presence duration (seconds)
MIN_PRESENCE_SECONDS = 10

# Face kitne seconds tak temporarily missing ho sakta hai
MAX_GAP_SECONDS = 2

# Tracking log check karo
if not os.path.exists(input_file):
    print("Error: tracking_log.csv file nahi mili!")
    exit()

df = pd.read_csv(input_file)

if df.empty:
    print("Tracking log empty hai. Pehle face_tracking.py run karo.")
    exit()

# Required columns check karo
required_columns = {"timestamp", "face_id"}

if not required_columns.issubset(df.columns):
    print("Error: CSV mein timestamp ya face_id column missing hai!")
    exit()

# Timestamps ko datetime mein convert karo
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp", "face_id"])

if df.empty:
    print("Valid tracking records nahi mile!")
    exit()

# Har face ki appearance times sort karo
df = df.sort_values(["face_id", "timestamp"])

attendance_records = []

for face_id, group in df.groupby("face_id"):
    times = group["timestamp"].drop_duplicates().sort_values()

    if times.empty:
        continue

    # Continuous presence sessions banao.
    # 2 seconds se bada gap aaye toh naya session.
    session_start = times.iloc[0]
    previous_time = times.iloc[0]
    total_presence = 0.0

    for current_time in times.iloc[1:]:
        gap = (current_time - previous_time).total_seconds()

        if gap <= MAX_GAP_SECONDS:
            total_presence += gap
        else:
            # Purana session complete
            session_duration = (
                previous_time - session_start
            ).total_seconds()

            total_presence += session_duration

            # Naya session start
            session_start = current_time

        previous_time = current_time

    # Last session ka duration add karo
    total_presence += (
        previous_time - session_start
    ).total_seconds()

    status = (
        "Present"
        if total_presence >= MIN_PRESENCE_SECONDS
        else "Absent"
    )

    attendance_records.append({
        "face_id": int(face_id),
        "presence_seconds": round(total_presence, 2),
        "status": status
    })

# Attendance CSV save karo
attendance_df = pd.DataFrame(attendance_records)
attendance_df.to_csv(output_file, index=False)

print("\nAttendance calculation complete!")
print(attendance_df.to_string(index=False))
print(f"\nAttendance saved to: {output_file}")
