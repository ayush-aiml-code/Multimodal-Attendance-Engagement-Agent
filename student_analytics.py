
import pandas as pd
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Input files
fusion_file = BASE_DIR / "multimodal_fusion.csv"
scores_file = BASE_DIR / "engagement_scores.csv"

# Output file
output_file = BASE_DIR / "student_analytics.csv"


def generate_student_analytics():
    # Check required files
    if not fusion_file.exists():
        print("Error: multimodal_fusion.csv not found.")
        print("Run multimodal_fusion.py first.")
        return

    if not scores_file.exists():
        print("Error: engagement_scores.csv not found.")
        print("Run engagement_score.py first.")
        return

    # Read data
    fusion = pd.read_csv(fusion_file)
    scores = pd.read_csv(scores_file)

    if fusion.empty or scores.empty:
        print("Error: Input files contain no data.")
        return

    # Calculate session-level attendance duration
    attendance_seconds = pd.to_numeric(
        fusion["presence_seconds"], errors="coerce"
    ).fillna(0).sum()

    # Calculate available engagement metrics
    score_values = pd.to_numeric(
        scores["engagement_score"], errors="coerce"
    ).dropna()

    if score_values.empty:
        print("Error: No valid engagement scores found.")
        return

    average_score = round(score_values.mean(), 2)
    minimum_score = round(score_values.min(), 2)
    maximum_score = round(score_values.max(), 2)
    score_variation = round(score_values.max() - score_values.min(), 2)

    # Reflective summary, not a grade or evaluation
    if score_variation <= 10:
        consistency = "Little variation in recorded scores"
    else:
        consistency = "Recorded scores varied during the available segments"

    if maximum_score - minimum_score > 20:
        trend = "A noticeable score difference appears across available segments"
    else:
        trend = "No large score difference appears in the available segments"

    # Prepare one personal session summary
    analytics = pd.DataFrame([{
        "session_attendance_seconds": round(attendance_seconds, 2),
        "average_prototype_score": average_score,
        "minimum_prototype_score": minimum_score,
        "maximum_prototype_score": maximum_score,
        "score_variation": score_variation,
        "score_consistency_summary": consistency,
        "activity_trend_summary": trend,
        "reflection_prompt": (
            "Think about what was happening during this session "
            "and which learning activities helped you participate."
        ),
        "data_note": (
            "Prototype summary from available signals. "
            "Scores do not measure grades, learning, or confirmed attention."
        )
    }])

    # Save analytics
    analytics.to_csv(output_file, index=False)

    print("Student analytics generated successfully!")
    print(analytics.to_string(index=False))
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    generate_student_analytics()

