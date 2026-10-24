
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import soundfile as sf

# Define project paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "audio_segments"
METADATA_FILE = BASE_DIR / "audio_metadata.csv"

# Configure audio processing
SAMPLE_RATE = 16000
SEGMENT_DURATION = 5

# Ask the user for an audio file
audio_path = input("Enter the audio file path: ").strip().strip('"')
audio_path = Path(audio_path)

if not audio_path.is_file():
    print("Error: Audio file not found.")
    raise SystemExit(1)

try:
    # Load audio as mono and standardize the sample rate
    audio, sr = librosa.load(
        str(audio_path),
        sr=SAMPLE_RATE,
        mono=True
    )
except Exception as error:
    print(f"Error loading audio: {error}")
    raise SystemExit(1)

if len(audio) == 0:
    print("Error: The audio file is empty.")
    raise SystemExit(1)

# Create the output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Calculate segment size in samples
segment_size = SAMPLE_RATE * SEGMENT_DURATION
metadata = []

# Split the audio into fixed-duration segments
for index, start in enumerate(range(0, len(audio), segment_size)):
    segment = audio[start:start + segment_size]

    start_time = start / SAMPLE_RATE
    end_time = (start + len(segment)) / SAMPLE_RATE

    segment_name = f"segment_{index + 1:03d}.wav"
    segment_path = OUTPUT_DIR / segment_name

    # Save the segment as a WAV file
    sf.write(segment_path, segment, SAMPLE_RATE)

    # Calculate amplitude measurements
    mean_amplitude = float(np.mean(np.abs(segment)))
    rms_amplitude = float(np.sqrt(np.mean(segment ** 2)))

    metadata.append({
        "segment": segment_name,
        "start_seconds": round(start_time, 3),
        "end_seconds": round(end_time, 3),
        "sample_rate": SAMPLE_RATE,
        "samples": len(segment),
        "mean_amplitude": round(mean_amplitude, 6),
        "rms_amplitude": round(rms_amplitude, 6)
    })

# Save the metadata
df = pd.DataFrame(metadata)
df.to_csv(METADATA_FILE, index=False)

print("\nAudio extraction completed!")
print(f"Duration: {len(audio) / SAMPLE_RATE:.2f} seconds")
print(f"Segments created: {len(metadata)}")
print(f"Audio segments folder: {OUTPUT_DIR}")
print(f"Metadata saved to: {METADATA_FILE}")
print(df.to_string(index=False))
