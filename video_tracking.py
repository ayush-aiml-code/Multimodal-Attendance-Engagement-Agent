
import csv
import math
from datetime import datetime, timedelta
from pathlib import Path

import cv2


def process_video(video_path, output_csv, cascade_path):
    """Track faces in a video and save detections to a CSV file."""

    video_path = Path(video_path)
    output_csv = Path(output_csv)
    cascade_path = Path(cascade_path)

    face_cascade = cv2.CascadeClassifier(str(cascade_path))

    if face_cascade.empty():
        raise ValueError("Could not load the face detection XML file.")

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError("Could not open the uploaded video.")

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Face tracking settings
    max_distance = 150
    max_missing_frames = 45
    distance_allowance = 5

    next_id = 1
    tracked_faces = {}
    frame_number = 0
    start_time = datetime.now()

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)

        if not fps or fps <= 0:
            fps = 25.0

        with output_csv.open(
            "w", newline="", encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(csv_file)
            writer.writerow([
                "timestamp", "face_id", "x", "y", "width", "height"
            ])

            while True:
                success, frame = cap.read()

                if not success:
                    break

                frame_number += 1

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=6,
                    minSize=(60, 60)
                )

                detections = []

                for x, y, w, h in faces:
                    detections.append({
                        "box": (int(x), int(y), int(w), int(h)),
                        "center": (
                            int(x + w // 2),
                            int(y + h // 2)
                        )
                    })

                # Match current detections to existing face IDs.
                candidates = []

                for face_id, info in tracked_faces.items():
                    frames_away = info["missing"] + 1
                    old_x, old_y = info["center"]
                    velocity_x, velocity_y = info["velocity"]

                    predicted_x = old_x + velocity_x * frames_away
                    predicted_y = old_y + velocity_y * frames_away

                    allowed_distance = (
                        max_distance
                        + info["missing"] * distance_allowance
                    )

                    for index, detection in enumerate(detections):
                        cx, cy = detection["center"]

                        distance = math.hypot(
                            cx - predicted_x,
                            cy - predicted_y
                        )

                        if distance < allowed_distance:
                            candidates.append(
                                (distance, face_id, index)
                            )

                candidates.sort(key=lambda item: item[0])

                assigned_ids = set()
                assigned_detections = set()
                updated_faces = {}
                detection_ids = {}

                for distance, face_id, index in candidates:
                    if face_id in assigned_ids:
                        continue

                    if index in assigned_detections:
                        continue

                    cx, cy = detections[index]["center"]
                    old_info = tracked_faces[face_id]

                    old_x, old_y = old_info["center"]
                    frames_away = old_info["missing"] + 1

                    observed_vx = (cx - old_x) / frames_away
                    observed_vy = (cy - old_y) / frames_away

                    old_vx, old_vy = old_info["velocity"]

                    velocity_x = 0.7 * old_vx + 0.3 * observed_vx
                    velocity_y = 0.7 * old_vy + 0.3 * observed_vy

                    updated_faces[face_id] = {
                        "center": (cx, cy),
                        "velocity": (velocity_x, velocity_y),
                        "missing": 0
                    }

                    assigned_ids.add(face_id)
                    assigned_detections.add(index)
                    detection_ids[index] = face_id

                # Assign new IDs to unmatched detections.
                for index, detection in enumerate(detections):
                    if index in assigned_detections:
                        continue

                    face_id = next_id
                    next_id += 1

                    updated_faces[face_id] = {
                        "center": detection["center"],
                        "velocity": (0.0, 0.0),
                        "missing": 0
                    }

                    detection_ids[index] = face_id

                # Retain temporarily missing faces for re-matching.
                for face_id, info in tracked_faces.items():
                    if face_id not in assigned_ids:
                        info["missing"] += 1

                        if info["missing"] <= max_missing_frames:
                            updated_faces[face_id] = info

                tracked_faces = updated_faces

                # Generate consistent timestamps for the video timeline.
                timestamp = (
                    start_time
                    + timedelta(seconds=frame_number / fps)
                ).isoformat(timespec="milliseconds")

                for index, detection in enumerate(detections):
                    x, y, w, h = detection["box"]
                    face_id = detection_ids[index]

                    writer.writerow([
                        timestamp, face_id, x, y, w, h
                    ])

                if frame_number % 30 == 0:
                    csv_file.flush()

    finally:
        cap.release()

    return {
        "frames_processed": frame_number,
        "tracking_csv": str(output_csv)
    }
