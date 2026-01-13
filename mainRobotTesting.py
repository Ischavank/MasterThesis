# main2.py
from qr_vision_RobotTesting import start_qr_vision, pause_robot, resume_robot
import time
import requests
from weather_api import get_q1h_de_bilt
from confidence import process_data
from model_usage import predict_flag
from plant_api import assess_plant_health
from sensorBM280 import bm_sensors
import datetime

def on_qr_detected(qr_data):
    print(f"\n🔍 Callback: QR '{qr_data}' detected! Starting analysis...")

    pause_robot()

    try:
        requests.get("http://192.168.4.1/js?json=" + '{"T":0}', timeout=0.2)
        print("🛑 Robot stopped")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Couldn't stop robot: {e}")

    time.sleep(1)  # Pause briefly

    print(f"QR input is: {qr_data}")
    print("QR analysis done, resume robot")

    time.sleep(2)
    if qr_data == "10":
        print("10 is detected, stop the program")
    else:
        resume_robot()

def main():
    print("[MAIN2] Starting dual-camera QR and red-object tracking system...")
    start_qr_vision(callback_on_qr=on_qr_detected)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[MAIN2] Shutdown")

if __name__ == "__main__":
    main()
