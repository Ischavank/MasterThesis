import requests
import time
from weather_api import get_q1h_de_bilt
from confidence import process_data
from model_usage import predict_flag
from plant_api import assess_plant_health
from sensorBM280 import bm_sensors
from robot_vision import start_robot_vision, pause_robot, resume_robot
import datetime

# Called when a plant is detected
def on_plant_detected(plant_label):
    print(f"\n Callback: Detected {plant_label}. Preparing to pause...")

    pause_robot()

    # Step 1: Stop robot briefly (send stop command)
    try:
        requests.get("http://192.168.4.1/js?json=" + '{"T":0}', timeout=0.2)
        print("Robot stopped for image capture.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Couldn't stop robot: {e}")

    # Step 2: Wait 1 second before doing anything
    time.sleep(1)

    # Step 3: Resume robot driving (it resumes via control thread anyway)
    print("Capturing photo and starting analysis...")

    # Step 4: Run full analysis while detection cooldown continues
    weather_api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVkZTIzYzExYjIyYzQ5NDlhYzZjYjQ3ZmQxMDUwY2UxIiwiaCI6Im11cm11cjEyOCJ9"
    qg = get_q1h_de_bilt(weather_api_key)

    humidity, pressure, temperature = bm_sensors()
    soilmoist = 35.1

    #plant_health_conf = process_data([qg, humidity, temperature, soilmoist])
    plant_health_conf, temp_conf, humi_conf, light_conf, soil_conf = process_data(
        [qg, humidity, temperature, soilmoist], return_all_conf=True
    )

    plant_id_api_key = "OfpKUFbJoqzbNWxeGriOfmZrtiRcNKc0I930dHks4vNK0jXLtm"
    api_health = 85.0  # STATIC — skip PlantNet
    flag = predict_flag(plant_health_conf, api_health)
    timestamp = datetime.datetime.now().isoformat()

    row = {
        "ID": next_id,
        "image_name": f"{plant_label}.jpg",
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "sun_light": q1h_lux,
        "soil_moist": soilmoist,
        "API_health": api_health,
        "API_water": api_water,
        "API_water_def": api_water_deficiency,
        "temp_conf": temp_conf,
        "humi_conf": humi_conf,
        "light_conf": light_conf,
        "soil_conf": soil_conf,
        "soil_validation": soil_validation,
        "model_conf": plant_health_conf,
        "final_tag": flag
    }

    log_plant_data(row)

    print(f"Plant Analysis Done | Flag: {flag} | Confidence: {plant_health_conf:.2f}")
    print("Waiting 3s before allowing next detection...")

    resume_robot()

if __name__ == "__main__":
    print("[MAIN] Starting vision system with plant detection...")
    start_robot_vision(callback_on_plant_detected=on_plant_detected)

    try:
        while True:
            time.sleep(1)  # Main loop remains responsive
    except KeyboardInterrupt:
        print("\n[MAIN] Shutting down.")
