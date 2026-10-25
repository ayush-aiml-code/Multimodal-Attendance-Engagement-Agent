
import pandas as pd
from pathlib import Path

# Get the project folder
BASE_DIR = Path(__file__).resolve().parent

# Input and output files
scores_file = BASE_DIR / "engagement_scores.csv"
audio_file = BASE_DIR / "audio_analysis.csv"
output_file = BASE_DIR / "teaching_suggestions.csv"


def generate_suggestions():
    suggestions = []

    # Check if engagement scores exist
    if not scores_file.exists():
        print("Error: engagement_scores.csv not found.")
        print("Run engagement_score.py first.")
        return

    scores = pd.read_csv(scores_file)

    if scores.empty:
        print("Engagement scores file is empty.")
        return

    # Analyze engagement levels
    average_score = scores["engagement_score"].mean()

    if average_score < 40:
        suggestions.append({
            "pattern": "Low engagement score",
            "observation": f"Average prototype score: {average_score:.1f}/100",
            "teaching_suggestion": (
                "Consider adding a short interactive activity, "
                "asking a question, or checking whether students "
                "need clarification."
            ),
            "reason": "The available rule-based score is low."
        })

    elif average_score < 70:
        suggestions.append({
            "pattern": "Moderate engagement score",
            "observation": f"Average prototype score: {average_score:.1f}/100",
            "teaching_suggestion": (
                "Consider checking student understanding with a "
                "quick question or short discussion."
            ),
            "reason": "The available rule-based score is moderate."
        })

    else:
        suggestions.append({
            "pattern": "High engagement score",
            "observation": f"Average prototype score: {average_score:.1f}/100",
            "teaching_suggestion": (
                "Review what was happening during this session "
                "segment and consider reusing effective teaching methods."
            ),
            "reason": "The available rule-based score is high."
        })

    # Analyze audio signal categories, if available
    if audio_file.exists():
        audio = pd.read_csv(audio_file)

        if not audio.empty and "category" in audio.columns:
            noisy_segments = audio[
                audio["category"].astype(str).str.contains(
                    "noise", case=False, na=False
                )
            ]

            if not noisy_segments.empty:
                suggestions.append({
                    "pattern": "Possible background noise",
                    "observation": (
                        f"{len(noisy_segments)} audio segment(s) "
                        "were labelled as possible noise."
                    ),
                    "teaching_suggestion": (
                        "Consider checking the room, microphone, "
                        "or background sounds before changing the lesson."
                    ),
                    "reason": (
                        "Audio category indicates possible noise; "
                        "this does not identify its source."
                    )
                })

    # Save suggestions
    result = pd.DataFrame(suggestions)
    result.to_csv(output_file, index=False)

    print("Teaching suggestions generated successfully!")
    print(result.to_string(index=False))
    print(f"\nSaved to: {output_file}")
    print("\nThese are optional suggestions, not instructions.")


if __name__ == "__main__":
    generate_suggestions()
