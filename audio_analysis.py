
import csv
from pathlib import Path

import numpy as np
import soundfile as sf

# Define project paths
BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio_segments"
OUTPUT_FILE = BASE_DIR / "audio_analysis.csv"
SUMMARY_FILE = BASE_DIR / "session_audio_summary.csv"

# Set thresholds for basic audio classification
SILENCE_THRESHOLD = 0.01
LOW_ENERGY_THRESHOLD = 0.05


def analyze_audio(file_path):
    # Read the audio file
    audio, sample_rate = sf.read(file_path, dtype="float32")

    # Convert stereo audio to mono
    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)

    # Handle empty audio files
    if len(audio) == 0:
        return None

    # Calculate basic audio features
    rms = float(np.sqrt(np.mean(audio ** 2)))
    peak_amplitude = float(np.max(np.abs(audio)))
    amplitude_variation = float(np.std(audio))

    # Calculate zero-crossing rate
    zero_crossings = np.sum(np.diff(np.signbit(audio)))
    zero_crossing_rate = float(
        zero_crossings / max(len(audio) - 1, 1)
    )

    # Estimate the sound category using simple thresholds
    if rms < SILENCE_THRESHOLD:
        category = "Silence or very low sound"
    elif rms < LOW_ENERGY_THRESHOLD:
        category = "Low-level sound or possible background noise"
    else:
        category = "Active sound - possible speech"

    # Calculate the duration of the segment
    duration = len(audio) / sample_rate

    return {
        "segment": Path(file_path).name,
        "duration_seconds": round(duration, 3),
        "sample_rate": sample_rate,
        "rms_energy": round(rms, 5),
        "peak_amplitude": round(peak_amplitude, 5),
        "amplitude_variation": round(amplitude_variation, 5),
        "zero_crossing_rate": round(zero_crossing_rate, 5),
        "category": category,
    }


def run_audio_analysis():
    # Find all WAV audio segments
    audio_files = sorted(AUDIO_DIR.glob("*.wav"))

    if not audio_files:
        raise FileNotFoundError(
            "No WAV files found. Run audio extraction first."
        )

    # Analyze each audio segment
    results = []

    for file_path in audio_files:
        try:
            result = analyze_audio(file_path)
            if result is not None:
                results.append(result)
        except (RuntimeError, ValueError, OSError) as error:
            print(f"Could not analyze {file_path.name}: {error}")

    if not results:
        raise ValueError("No audio segments could be analyzed.")

    # Save segment-level analysis
    fieldnames = list(results[0].keys())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Calculate session-level summary
    total_segments = len(results)

    silence_count = sum(
        row["category"] == "Silence or very low sound"
        for row in results
    )
    low_level_count = sum(
        row["category"] == "Low-level sound or possible background noise"
        for row in results
    )
    active_count = sum(
        row["category"] == "Active sound - possible speech"
        for row in results
    )

    average_rms = float(np.mean([row["rms_energy"] for row in results]))
    total_duration = float(
        sum(row["duration_seconds"] for row in results)
    )

    summary = {
        "total_segments": total_segments,
        "total_duration_seconds": round(total_duration, 3),
        "average_rms_energy": round(average_rms, 5),
        "silence_segments": silence_count,
        "low_level_sound_segments": low_level_count,
        "active_sound_segments": active_count,
        "active_sound_percentage": round(
            active_count / total_segments * 100, 2
        ),
    }

    with open(
        SUMMARY_FILE, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    return results, summary


if __name__ == "__main__":
    try:
        results, summary = run_audio_analysis()

        print("\nAudio analysis complete!")
        print("\nSegment-level results:")

        for row in results:
            print(
                f'{row["segment"]}: {row["category"]}, '
                f'RMS={row["rms_energy"]}'
            )

        print("\nSession summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")

        print(f"\nDetailed results saved to: {OUTPUT_FILE}")
        print(f"Session summary saved to: {SUMMARY_FILE}")

    except Exception as error:
        print(f"Error: {error}")
