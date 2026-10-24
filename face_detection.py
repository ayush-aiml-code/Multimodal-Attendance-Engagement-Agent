import cv2
import os
# Load face detection XML file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

xml_path = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(xml_path)

print("XML file path:", xml_path)
print("XML loaded:", not face_cascade.empty())

# Check whether XML file loaded correctly
if face_cascade.empty():
    print("Error: Face detection XML file load nahi hui!")
    exit()

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Webcam open nahi ho pa raha!")
    exit()

print("Face detection start ho gaya. Exit ke liye Q press karo.")

while True:
    success, frame = cap.read()

    if not success:
        print("Webcam se video nahi mil rahi!")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw rectangle around each detected face
    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face Detected",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Detection - Press Q to Exit", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

