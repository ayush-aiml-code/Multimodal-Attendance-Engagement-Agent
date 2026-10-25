
import cv2
import os
import csv
import math
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

xml_path = os.path.join(
    BASE_DIR, "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(xml_path)

if face_cascade.empty():
    print("Error: Face detection XML could not be loaded!")
    raise SystemExit(1)

# Choose input: "webcam" or "video"
INPUT_MODE = "video"

# If using a video, put its filename here
VIDEO_FILE = "classroom.mp4"

if INPUT_MODE == "webcam":
    cap = cv2.VideoCapture(0)
elif INPUT_MODE == "video":
    video_path = os.path.join(BASE_DIR, VIDEO_FILE)
    cap = cv2.VideoCapture(video_path)
else:
    print("Invalid INPUT_MODE!")
    raise SystemExit(1)

if not cap.isOpened():
    print("Error: Could not open the selected input.")
    raise SystemExit(1)

next_id = 1
tracked_faces = {}

MAX_DISTANCE = 150
MAX_MISSING_FRAMES = 45
DISTANCE_ALLOWANCE_PER_MISSING_FRAME = 5

csv_path = os.path.join(BASE_DIR, "tracking_log.csv")

try:
    with open(
        csv_path, "w", newline="", encoding="utf-8"
    ) as csv_file:

        writer = csv.writer(csv_file)
        writer.writerow([
            "timestamp", "face_id", "x", "y", "width", "height"
        ])

        frame_number = 0
        print("Face tracking started. Press Q to exit.")

        while True:
            success, frame = cap.read()

            if not success:
                if INPUT_MODE == "video":
                    print("Video finished or frame could not be read.")
                else:
                    print("Could not read webcam frame.")
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

            for (x, y, w, h) in faces:
                detections.append({
                    "box": (x, y, w, h),
                    "center": (x + w // 2, y + h // 2)
                })

            candidates = []

            for face_id, info in tracked_faces.items():
                frames_away = info["missing"] + 1
                old_x, old_y = info["center"]
                velocity_x, velocity_y = info["velocity"]

                predicted_x = old_x + velocity_x * frames_away
                predicted_y = old_y + velocity_y * frames_away

                allowed_distance = (
                    MAX_DISTANCE
                    + info["missing"]
                    * DISTANCE_ALLOWANCE_PER_MISSING_FRAME
                )

                for index, detection in enumerate(detections):
                    cx, cy = detection["center"]
                    distance = math.hypot(
                        cx - predicted_x, cy - predicted_y
                    )

                    if distance < allowed_distance:
                        candidates.append((distance, face_id, index))

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

            for index, detection in enumerate(detections):
                if index in assigned_detections:
                    continue

                face_id = next_id
                next_id += 1
                cx, cy = detection["center"]

                updated_faces[face_id] = {
                    "center": (cx, cy),
                    "velocity": (0.0, 0.0),
                    "missing": 0
                }

                detection_ids[index] = face_id

            for face_id, info in tracked_faces.items():
                if face_id not in assigned_ids:
                    info["missing"] += 1
                    if info["missing"] <= MAX_MISSING_FRAMES:
                        updated_faces[face_id] = info

            tracked_faces = updated_faces

            # Use video timestamps for saved videos
            if INPUT_MODE == "video":
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps and fps > 0:
                    timestamp = datetime.fromtimestamp(
                        os.path.getmtime(video_path)
                    ).isoformat(timespec="milliseconds")
                    video_seconds = frame_number / fps
                    timestamp = (
                        f"{timestamp[:10]}T"
                        f"{int(video_seconds // 3600):02d}:"
                        f"{int((video_seconds % 3600) // 60):02d}:"
                        f"{video_seconds % 60:06.3f}"
                    )
                else:
                    timestamp = datetime.now().isoformat(
                        timespec="milliseconds"
                    )
            else:
                timestamp = datetime.now().isoformat(
                    timespec="milliseconds"
                )

            for index, detection in enumerate(detections):
                x, y, w, h = detection["box"]
                face_id = detection_ids[index]

                cv2.rectangle(
                    frame, (x, y), (x + w, y + h), (0, 255, 0), 2
                )
                cv2.putText(
                    frame, f"Face ID: {face_id}",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )

                writer.writerow([
                    timestamp, face_id, x, y, w, h
                ])

            cv2.putText(
                frame, f"Faces detected: {len(detections)}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 0), 2
            )

            cv2.imshow("Face Tracking - Press Q to Exit", frame)

            if frame_number % 30 == 0:
                csv_file.flush()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    cap.release()
    cv2.destroyAllWindows()

print("Face tracking completed.")
print(f"Tracking data saved to: {csv_path}")
