
import pandas as pd
from pathlib import Path

# Get the folder where this Python file is saved
BASE_DIR = Path(__file__).resolve().parent

fusion_file = BASE_DIR / "multimodal_fusion.csv"
audio_file = BASE_DIR / "audio_analysis.csv"
output_file = BASE_DIR / "engagement_scores.csv"

# Check that the required files exist
if not fusion_file.exists() or not audio_file.exists():
    print("Error: Required CSV files were not found.")
    print("Make sure both CSV files are in the project folder.")
    raise SystemExit(1)

# Read the existing data
fusion = pd.read_csv(fusion_file)
audio = pd.read_csv(audio_file)

if fusion.empty or audio.empty:
    print("Error: One or both CSV files contain no data.")
    raise SystemExit(1)

# Use the first session-level fusion record
session = fusion.iloc[0]

# Define transparent scoring rules
presence_score = 50 if session["attendance_status"] == "Present" else 0

# Active sound contributes up to 50 points.
# This measures sound activity, NOT speech or attention.
audio_activity = max(0, min(100, float(session["active_sound_percentage"])))
audio_score = audio_activity * 0.5

# Combine the available signals
engagement_score = round(presence_score + audio_score, 2)

# Keep the score between 0 and 100
engagement_score = max(0, min(100, engagement_score))

# Assign a rule-based category
if engagement_score >= 70:
    engagement_level = "High"
elif engagement_score >= 40:
    engagement_level = "Moderate"
else:
    engagement_level = "Low"

# Create one result for each available audio segment.
# The face-presence value is session-level, not interval-level.
results = []

for _, segment in audio.iterrows():
    results.append({
        "segment": segment["segment"],
        "duration_seconds": segment["duration_seconds"],
        "face_id": session["face_id"],
        "attendance_status": session["attendance_status"],
        "session_presence_seconds": session["presence_seconds"],
        "rms_energy": segment["rms_energy"],
        "audio_category": segment["category"],
        "presence_score": presence_score,
        "audio_score": round(audio_score, 2),
        "engagement_score": engagement_score,
        "engagement_level": engagement_level,
        "score_scope": "Prototype; limited available signals"
    })

# Save the results
scores = pd.DataFrame(results)
scores.to_csv(output_file, index=False)

print("Engagement score calculation complete!")
print(scores.to_string(index=False))
print(f"\nSaved to: {output_file}")
print("\nNote: This score is a rule-based prototype, not a verified")
print("measurement of student attention or learning engagement.")
print("Movement and inactivity data are not available yet.")
