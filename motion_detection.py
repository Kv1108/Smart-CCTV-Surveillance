# CCTV.py - Optimized face & body detection with video recording

import cv2
import time
import datetime
import os
from utils import ensure_folder_exists

# ------------------ SETTINGS ------------------
SECONDS_TO_RECORD_AFTER_DETECTION = 5
VIDEO_FOLDER = "recorded_videos"
DETECTION_INTERVAL = 3  # Detect every 3 frames
MIN_CONTOUR_AREA = 1000  # Optional for motion refinement

# Ensure folder exists
ensure_folder_exists(VIDEO_FOLDER)

# ------------------ VIDEO SETUP ------------------
cap = cv2.VideoCapture(0)
frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

# ------------------ CASCADES ------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

# ------------------ DETECTION STATE ------------------
detection = False
timer_started = False
detection_stopped_time = None
out = None
frame_count = 0

# ------------------ MAIN LOOP ------------------
while True:
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces, bodies = [], []

    # Only detect every few frames to save CPU
    if frame_count % DETECTION_INTERVAL == 0:
        gray_small = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
        faces = face_cascade.detectMultiScale(gray_small, 1.1, 4)
        bodies = body_cascade.detectMultiScale(gray_small, 1.1, 4)

    objects_detected = len(faces) + len(bodies) > 0

    # ------------------ RECORDING LOGIC ------------------
    if objects_detected:
        if not detection:
            detection = True
            timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            video_path = os.path.join(VIDEO_FOLDER, f"{timestamp}.mp4")
            out = cv2.VideoWriter(video_path, fourcc, 20, frame_size)
            print(f"Started Recording: {video_path}")
        timer_started = False
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                out = None
                print("Stopped Recording!")
        else:
            timer_started = True
            detection_stopped_time = time.time()

    # Write frames if detection active
    if detection and out:
        out.write(frame)

    # ------------------ DRAW RECTANGLES ------------------
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x*2, y*2), (x*2 + w*2, y*2 + h*2), (255, 0, 0), 3)
    for (x, y, w, h) in bodies:
        cv2.rectangle(frame, (x*2, y*2), (x*2 + w*2, y*2 + h*2), (0, 255, 0), 3)

    # ------------------ DISPLAY ------------------
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord("q"):
        break

# ------------------ CLEANUP ------------------
if out:
    out.release()
cap.release()
cv2.destroyAllWindows()
