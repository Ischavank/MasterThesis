
# qr_vision.py
import cv2
import time
import threading
import requests
from picamera2 import Picamera2
from pyzbar.pyzbar import decode
from PIL import Image
from typing import Callable
import numpy as np
import os
import sys
import select

# State
seen_qrs = set()
last_qr_time = 0
QR_COOLDOWN = 3  # seconds
current_center_x = None
lock = threading.Lock()
pause_movement = False
show_feed_0 = False
show_feed_1 = False

def camera_thread(callback_on_qr):
    global current_center_x, last_qr_time, seen_qrs

    cam0 = Picamera2(0)
    cam1 = Picamera2(1)

    cam0.configure(cam0.create_preview_configuration())
    cam1.configure(cam1.create_preview_configuration())

    cam0.start()
    cam1.start()

    time.sleep(2)

    try:
        while True:
            # --- Camera 0: Red Object Detection ---
            frame0 = cam0.capture_array()
            frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(frame0, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            found = False
            frame_center = frame0.shape[1] // 2

            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    object_center = x + w // 2
                    with lock:
                        current_center_x = object_center
                    found = True
                    if show_feed_0:
                        cv2.rectangle(frame0, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    break

            if not found:
                with lock:
                    current_center_x = None

            # Show live feed if enabled
            if show_feed_0:
                resized = cv2.resize(frame0, (640, 480))  # Resize for better display
                cv2.imshow("Camera 0 Feed", resized)

            # --- Camera 1: QR Code Detection ---
            frame1 = cam1.capture_array()
            frame1_bgr = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)
            decoded = decode(Image.fromarray(frame1_bgr))
            now = time.time()

            # --- Automatic QR detection ---
            if decoded and now - last_qr_time > QR_COOLDOWN:
                for obj in decoded:
                    data = obj.data.decode()
                    if data not in seen_qrs:
                        seen_qrs.add(data)
                        last_qr_time = now
                        label = f"qr_{int(now)}"

                        file_path = f"photos2/{label}.jpg"
                        cam1.capture_file(file_path)
                        print(f"📷 QR Detected: {data}")
                        if callback_on_qr:
                            threading.Thread(target=callback_on_qr, args=(data,)).start()

            # --- Manual trigger with 't' + Enter ---
#            print("🧪 Press 't' + Enter to simulate a QR detection.")
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.readline().strip()
                if key.lower() == "t":
                    now = time.time()
                    simulated_data = f"manual_qr_{int(now)}"
                    label = f"qr_{int(now)}"
                    file_path = f"photos2/{label}.jpg"
                    cam1.capture_file(file_path)
                    print(f"🧪 [Manual Trigger] Simulated QR Detected: {simulated_data}")
                    if callback_on_qr:
                        threading.Thread(target=callback_on_qr, args=(simulated_data,)).start()
            time.sleep(0.05)


            if show_feed_1:
                for obj in decoded:
                    x, y, w, h = obj.rect
                    cv2.rectangle(frame1_bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame1_bgr, obj.data.decode(), (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                resized = cv2.resize(frame1_bgr, (640, 480))
                cv2.imshow("Camera 1 QR Feed", resized)
                cv2.waitKey(1)

    except KeyboardInterrupt:
        cam0.stop()
        cam1.stop()

def control_thread():
    global current_center_x
    Kp = 0.0002
    base_speed = 0.05
    frame_center = 640 // 2  # Assuming 640px wide

    try:
        while True:
            with lock:
                cx = current_center_x

            if not pause_movement and cx is not None:
                error = cx - frame_center
                correction = Kp * error
                L_speed = (base_speed - correction) * -1
                R_speed = (base_speed + correction) * -1

                command = f'{{"T":1,"L":{L_speed},"R":{R_speed}}}'
                url = "http://192.168.4.1/js?json=" + command
                try:
                    requests.get(url, timeout=0.2)
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Movement: {e}")
            else:
                # No red object → optional: slow down or stop
                pass

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

def pause_robot():
    global pause_movement
    pause_movement = True

def resume_robot():
    global pause_movement
    pause_movement = False

def start_qr_vision(callback_on_qr: Callable[[str], None]):
    t1 = threading.Thread(target=camera_thread, args=(callback_on_qr,))
    t2 = threading.Thread(target=control_thread)
    t1.start()
    t2.start()
