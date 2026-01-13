"""
main.py

Entry point for the greenhouse robot system

The robot follows a tape line and triggers an analysis pipeline when a QR is detected
1) Pause robot motion
2) Read local sensor (BME280)
3) Retrieve external weather data (API)
4) Capture plant image and analyise via Plant API (optional in testing mode)
5) Add soilmoisture content placeholder value
5) Append a row to a CSV log file
6) Resume robot (unless a stop QR ID is detected)

Hardware assumptions:
- Raspberry Pi with two cameras (line following + plant/QR camera)
- BME280 sensor connected
- Robot chassis accessible via HTTP endpoint (192.168.4.1)

"""


from robot_vision_SystemTesting import start_qr_vision, pause_robot, resume_robot
import time
import requests
import csv
from weather_api import get_q1h_de_bilt
from confidence import process_data
from model_usage import predict_flag
from plant_api import assess_plant_health
from sensorBM280 import bm_sensors
import datetime

testing = False # True/False

# File paths
photo_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos5"
raw_data_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_SystemTesting.csv"



if testing:
    print("Important, in testing state, so no data logging")

def on_qr_detected(photo_label):
    qr_data = photo_label.split('_')[1]
    print(f"\nCallback: R {qr_data} detected! Starting analysis...")

    # Pausing robot
    pause_robot()
    try:
        requests.get("http://192.168.4.1/js?json=" + '{"T":0}', timeout=0.2)
        print("Robot stopped")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Couldn't stop robot: {e}")

    time.sleep(1)  # Pause briefly

        # Get sensor data
    humidity, pressure, temperature = bm_sensors()

        # Get weather data
    q1h_lux = get_q1h_de_bilt("eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVkZTIzYzExYjIyYzQ5NDlhYzZjYjQ3ZmQxMDUwY2UxIiwiaCI6Im11cm11cjEyOCJ9")

        # Taking photo and analyzing
    image_path = f"{photo_path}/{photo_label}.jpg"
    if not testing:
        plant_id_api_key = "93j1F4tg9Vq1QIKKo9JoY6hEiT2JGZxV8nMplZvIJYVeqqWDAh"
        data = assess_plant_health(image_path, plant_id_api_key, latitude=None, longitude=None)
        if data['is_healthy_probability'] == None:
            api_health = None
            api_water = None
            api_water_deficiency = None
            print("No plant detected")
        else:
            api_health = round(data['is_healthy_probability']*100,1)
            api_water = round(data['water_realted_issue']['probability']*100,1) #water related problem
            api_water_deficiency = round(data['water_deficiency']['probability']*100,1) #water deficiency
    else:
        api_health = 85.0  # Placeholder or static
        api_water = 50
        api_water_deficiency = 50

        # Soil moist conversion
    if api_health == None:
        soilmoist = 'testing'
    elif api_health < 70:
        soilmoist = 10
    elif api_health > 69:
        soilmoist = 60



        # Data logging
    row = {
        "ID": qr_data,
        "image_name": f"{photo_label}",
        "temperature": temperature,
        "humidity": humidity,
        "sun_light": q1h_lux,
        "soil_moist": soilmoist,
        "API_health": api_health,
        "API_water": api_water,
        "API_water_def": api_water_deficiency,
    }

    headers = ["ID", "image_name", "temperature", "humidity", "sun_light", "soil_moist",
               "API_health", "API_water", "API_water_def"]

    with open(raw_data_path, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(row)
    print("data logged")

    time.sleep(1)

    # Resuming or ending the robot
    if qr_data == "10":
        print("10 is detected, stop the program")
    else:
        print("Resuming")
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
