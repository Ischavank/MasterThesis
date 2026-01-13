# main2.py
from qr_vision import start_qr_vision, pause_robot, resume_robot
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

    print("📸 Analyzing environment and collecting data...")

    weather_api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVkZTIzYzExYjIyYzQ5NDlhYzZjYjQ3ZmQxMDUwY2UxIiwiaCI6Im11cm11cjEyOCJ9"
    q1h_lux = get_q1h_de_bilt(weather_api_key)

    humidity, pressure, temperature = bm_sensors()
    soilmoist = 35.1  # or replace with sensor reading

    # Use extended process_data
    plant_health_conf, temp_conf, humi_conf, light_conf, soil_conf = process_data(
        [q1h_lux, humidity, temperature, soilmoist], return_all_conf=True
    )

    plant_id_api_key = "OfpKUFbJoqzbNWxeGriOfmZrtiRcNKc0I930dHks4vNK0jXLtm"
    api_health = 85.0  # Can be static or from another service
    flag = predict_flag(plant_health_conf, api_health)
    timestamp = datetime.datetime.now().isoformat()

    # Use QR as label for image_name field
    image_label = f"qr_{qr_data}_{int(time.time())}"

    row = {
        "image_name": f"{image_label}.jpg",
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "sun_light": q1h_lux,
        "soil_moist": soilmoist,
        "API_conf": api_health,
        "temp_conf": temp_conf,
        "humi_conf": humi_conf,
        "light_conf": light_conf,
        "soil_conf": soil_conf,
        "model_conf": plant_health_conf,
        "final_tag": flag
    }

    log_plant_data(row)

    print(f"✅ QR Analysis Done | Flag: {flag} | Confidence: {plant_health_conf:.2f}\n")

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
