import cv2
import numpy as np
import threading
import time
import os
import requests
from picamera2 import Picamera2
from ultralytics import YOLO
from typing import Callable
import sys
import select

# Create folder for photos if missing
os.makedirs("photos", exist_ok=True)

# Detection model and plant class settings
model = YOLO("yolov8n.pt")
PLANT_CLASS_IDS = [58, 16]
DETECTION_INTERVAL = 5

# Global/shared state
current_center_x = None
camera1 = None
lock = threading.Lock()
last_detection_time = 0
DETECTION_COOLDOWN = 3  # seconds
pause_movement = False

def is_plant_detected(results):
    for result in results:
        for cls_id in result.boxes.cls:
            if int(cls_id) in PLANT_CLASS_IDS:
                return True
    return False

def camera_thread(callback_on_plant):
    global current_center_x, camera1, last_detection_time

    cam0 = Picamera2(0)
    cam1 = Picamera2(1)

    cam0.configure(cam0.create_preview_configuration())
    cam1.configure(cam1.create_preview_configuration(main={"size": (320, 240)}))

    cam0.start()
    cam1.start()

    frame_count = 0

    try:
        while True:
            frame0 = cam0.capture_array()
            frame1 = cam1.capture_array()

            frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)

            # --- Track red object in frame0 ---
            hsv0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(hsv0, np.array([0, 100, 100]), np.array([10, 255, 255]))
            mask2 = cv2.inRange(hsv0, np.array([160, 100, 100]), np.array([180, 255, 255]))
            mask = mask1 + mask2

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            found = False
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    object_center = x + (w // 2)
                    with lock:
                        current_center_x = object_center
                        camera1 = cam1
                    found = True
                    break
            if not found:
                with lock:
                    current_center_x = None
                    camera1 = cam1

            # --- Detect plants on cam1 every N frames ---
# --- Detect plants on cam1 every N frames ---
            if frame_count % DETECTION_INTERVAL == 0:
                now = time.time()
                if now - last_detection_time >= DETECTION_COOLDOWN:
                    results = model(frame1, classes=PLANT_CLASS_IDS, verbose=False)
                    if is_plant_detected(results):
                        label = f"plant_{int(now)}"
                        file_path = f"photos/{label}.jpg"
                        cam1.capture_file(file_path)
                        print(f"🌿 Plant detected! Photo saved: {file_path}")
                        last_detection_time = now

                        if callback_on_plant:
                            threading.Thread(target=callback_on_plant, args=(label,)).start()
                    else:
                        abcdefg = 1
#                        print("[DETECT] No plant found this cycle.")
                else:
                    print(f"[COOLDOWN] Skipping detection — {int(DETECTION_COOLDOWN - (now - last_detection_time))}s left.")


#                print("📸 Press 't' + Enter to manually simulate a plant detection.")
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.readline().strip()
                if key.lower() == "t":
                    now = time.time()
                    label = f"manual_trigger_{int(now)}"
                    file_path = f"photos/{label}.jpg"
                    cam1.capture_file(file_path)
                    print(f"🧪 [Manual Trigger] Simulated plant detection. Photo saved: {file_path}")
        
                    if callback_on_plant:
                        threading.Thread(target=callback_on_plant, args=(label,)).start()

            frame_count += 1
            time.sleep(0.01)

    except KeyboardInterrupt:
        cam0.stop()
        cam1.stop()

def control_thread():
    global current_center_x, camera1

    Kp = 0.0001
    base_speed = 0.05
    frame_center = 640 // 2

    try:
        while True:
            with lock:
                cx = current_center_x

            if not pause_movement and cx is not None:
                error = cx - frame_center
                correction = Kp * error
                L_speed = base_speed + correction
                R_speed = base_speed - correction

                command = f'{{"T":1,"L":{L_speed},"R":{R_speed}}}'
                url = "http://192.168.4.1/js?json=" + command
                try:
                    requests.get(url, timeout=0.2)
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Movement request failed: {e}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

def pause_robot():
    global pause_movement
    pause_movement = True

def resume_robot():
    global pause_movement
    pause_movement = False

def start_robot_vision(callback_on_plant_detected: Callable[[str], None]):
    t1 = threading.Thread(target=camera_thread, args=(callback_on_plant_detected,))
    t2 = threading.Thread(target=control_thread)
    t1.start()
    t2.start()
