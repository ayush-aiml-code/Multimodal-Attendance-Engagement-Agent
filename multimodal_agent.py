
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ATTENDANCE_FILE = BASE_DIR / "attendance.csv"
AUDIO_SUMMARY_FILE = BASE_DIR / "session_audio_summary.csv"
OUTPUT_FILE = BASE_DIR / "engagement_insights.csv"


def generate_insights():
    insights = []

    # Analyze attendance data
    if ATTENDANCE_FILE.exists():
        attendance = pd.read_csv(ATTENDANCE_FILE)

        if not attendance.empty and "status" in attendance.columns:
            present_count = int(
                (attendance["status"] == "Present").sum()
            )
            total_faces = len(attendance)

            insights.append({
                "metric": "Attendance",
                "value": f"{present_count}/{total_faces}",
                "insight": (
                    "Attendance records are available."
                    if total_faces > 0
                    else "No attendance records are available."
                )
            })
    else:
        insights.append({
            "metric": "Attendance",
            "value": "Unavailable",
            "insight": "Run the attendance module first."
        })

    # Analyze audio session summary
    if AUDIO_SUMMARY_FILE.exists():
        audio = pd.read_csv(AUDIO_SUMMARY_FILE)

        if not audio.empty:
            row = audio.iloc[0]
            active = float(row.get("active_sound_percentage", 0))
            silence = int(row.get("silence_segments", 0))

            if active >= 50:
                message = "High audio activity detected."
            elif silence > 0:
                message = "Silence was detected in some audio segments."
            else:
                message = (
                    "Low or uncertain audio activity. "
                    "This does not confirm student engagement."
                )

            insights.append({
                "metric": "Audio Activity",
                "value": f"{active:.1f}% active sound",
                "insight": message
            })
    else:
        insights.append({
            "metric": "Audio Activity",
            "value": "Unavailable",
            "insight": "Run audio_analysis.py first."
        })

    # Save generated insights
    result = pd.DataFrame(insights)
    result.to_csv(OUTPUT_FILE, index=False)

    print("\nMultimodal Agent Results")
    print(result.to_string(index=False))
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_insights()
