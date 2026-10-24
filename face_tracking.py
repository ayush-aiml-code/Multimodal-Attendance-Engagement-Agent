import cv2
import os
import csv
import time
import math
from datetime import datetime

# XML file ka path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(
    BASE_DIR, "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(xml_path)

if face_cascade.empty():
    print("Error: XML file load nahi hui!")
    exit()

# Webcam start
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Webcam open nahi ho pa raha!")
    exit()

# Tracking settings
next_id = 1
tracked_faces = {}
MAX_DISTANCE = 150
MAX_MISSING_FRAMES = 20

# CSV file
csv_file = open(
    os.path.join(BASE_DIR, "tracking_log.csv"),
    "w",
    newline="",
    encoding="utf-8"
)

writer = csv.writer(csv_file)
writer.writerow([
    "timestamp", "face_id", "x", "y", "width", "height"
])

frame_number = 0

print("Tracking start! Exit ke liye Q press karo.")

while True:
    success, frame = cap.read()

    if not success:
        print("Webcam se video nahi mil rahi!")
        break

    frame_number += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(60, 60)
    )

    # Har detected face ka center point
    detections = []

    for (x, y, w, h) in faces:
        center_x = x + w // 2
        center_y = y + h // 2
        detections.append((x, y, w, h, center_x, center_y))

    # Is frame mein assign hui IDs
    assigned_ids = set()
    updated_faces = {}

    # Existing IDs se detected faces match karo
    for detection in detections:
        x, y, w, h, cx, cy = detection
        best_id = None
        best_distance = MAX_DISTANCE

        for face_id, info in tracked_faces.items():
            if face_id in assigned_ids:
                continue

            old_x, old_y = info["center"]
            distance = math.sqrt(
                (cx - old_x) ** 2 + (cy - old_y) ** 2
            )

            if distance < best_distance:
                best_distance = distance
                best_id = face_id

        # Match nahi mila toh nayi ID do
        if best_id is None:
            best_id = next_id
            next_id += 1

        assigned_ids.add(best_id)

        updated_faces[best_id] = {
            "center": (cx, cy),
            "missing": 0
        }

        # Screen par rectangle aur ID
        cv2.rectangle(
            frame, (x, y), (x + w, y + h), (0, 255, 0), 2
        )

        cv2.putText(
            frame, f"Face ID: {best_id}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2
        )

        # Tracking details CSV mein likho
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            best_id, x, y, w, h
        ])

    # Jo faces kuch frames ke liye missing hain,
    # unki IDs temporarily preserve karo
    for face_id, info in tracked_faces.items():
        if face_id not in assigned_ids:
            info["missing"] += 1

            if info["missing"] <= MAX_MISSING_FRAMES:
                updated_faces[face_id] = info

    tracked_faces = updated_faces

    cv2.imshow("Face Tracking - Press Q to Exit", frame)

    if frame_number % 30 == 0:
        csv_file.flush()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
csv_file.close()
cv2.destroyAllWindows()

print("Tracking complete!")
print("Tracking data tracking_log.csv is saved")
