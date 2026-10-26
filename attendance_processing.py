
from pathlib import Path

import pandas as pd


MIN_PRESENCE_SECONDS = 10
MAX_GAP_SECONDS = 2


def calculate_attendance(input_file, output_file):
    """Calculate attendance from face-tracking records."""

    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.exists():
        raise FileNotFoundError("tracking_log.csv file nahi mili.")

    df = pd.read_csv(input_file)

    if df.empty:
        raise ValueError("Tracking log empty hai.")

    required_columns = {"timestamp", "face_id"}

    if not required_columns.issubset(df.columns):
        raise ValueError("CSV mein timestamp ya face_id missing hai.")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )
    df = df.dropna(subset=["timestamp", "face_id"])

    if df.empty:
        raise ValueError("Valid tracking records nahi mile.")

    df = df.sort_values(["face_id", "timestamp"])
    attendance_records = []

    for face_id, group in df.groupby("face_id"):
        times = group["timestamp"].drop_duplicates().sort_values()

        if times.empty:
            continue

        total_presence = 0.0

        for i in range(1, len(times)):
            gap = (
                times.iloc[i] - times.iloc[i - 1]
            ).total_seconds()

            if 0 < gap <= MAX_GAP_SECONDS:
                total_presence += gap

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

    attendance_df = pd.DataFrame(
        attendance_records,
        columns=["face_id", "presence_seconds", "status"]
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    attendance_df.to_csv(output_file, index=False)

    return attendance_df
