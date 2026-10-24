
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

ATTENDANCE_FILE = BASE_DIR / "attendance.csv"
AUDIO_FILE = BASE_DIR / "session_audio_summary.csv"
OUTPUT_FILE = BASE_DIR / "multimodal_fusion.csv"


def create_multimodal_fusion():
    if not ATTENDANCE_FILE.exists():
        print("Error: attendance.csv not found.")
        return

    if not AUDIO_FILE.exists():
        print("Error: session_audio_summary.csv not found.")
        return

    attendance = pd.read_csv(ATTENDANCE_FILE)
    audio = pd.read_csv(AUDIO_FILE)

    if attendance.empty or audio.empty:
        print("Error: One or more input files are empty.")
        return

    audio_row = audio.iloc[0]

    fused_records = []

    for _, row in attendance.iterrows():
        presence = float(row.get("presence_seconds", 0))
        status = str(row.get("status", "Unknown"))

        active_percentage = float(
            audio_row.get("active_sound_percentage", 0)
        )
        average_rms = float(
            audio_row.get("average_rms_energy", 0)
        )

        fused_records.append({
            "face_id": row.get("face_id", -1),
            "presence_seconds": presence,
            "attendance_status": status,
            "audio_duration_seconds": float(
                audio_row.get("total_duration_seconds", 0)
            ),
            "average_rms_energy": average_rms,
            "active_sound_percentage": active_percentage,
            "fusion_status": "Combined"
        })

    fused = pd.DataFrame(fused_records)
    fused.to_csv(OUTPUT_FILE, index=False)

    print("Multimodal signal fusion complete!")
    print(fused.to_string(index=False))
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_multimodal_fusion()
