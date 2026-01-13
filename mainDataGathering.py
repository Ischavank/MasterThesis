import time
import datetime
import threading
import select
import sys
import os
from picamera2 import Picamera2
from sensorBM280 import bm_sensors
from weather_api import get_q1h_de_bilt
from data_logger import log_plant_data_processed, log_plant_data_raw
from confidence import process_data
from model_usage import predict_flag
from soil_moist import read_adc
from plant_api import assess_plant_health

testing = False # True False

# File paths
photo_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos4"
raw_data_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_raw1.csv"
processed_data_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_processed1.csv"

# Camera setup
cam1 = Picamera2(1)
cam1.configure(cam1.create_preview_configuration(main={"size": (320, 240)}))
cam1.start()

if testing:
    print("")
    print("IMPORTANT, in testing state, so no data logging")

while True:
    place1 = input("At which place are we? Home (h), Uni (u) or Outside (o)? ").strip().lower()
    if place1 in ['h', 'u', 'o']:
        place_dict = {'h':'Home', 'u':'Uni', 'o':'Outside'}
        place = place_dict[place1]
        print(f"Tag saved: {place}")
        break
    else:
        print("Invalid input. Please enter 'h', 'u', or 'o'.")

print("📷 Ready for manual data capture.")
print("🟢 Press 't' + Enter to take a snapshot and log sensor data.")
print("🔴 Press Ctrl+C to exit.\n")

def capture_and_log(place):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    label = timestamp + '_' + place
    image_path = f"{photo_path}/{label}.jpg"

    # Take photo
    if not testing:
        cam1.capture_file(image_path)
        print(f"📸 Image saved: {image_path}")

    # Get sensor data
    humidity, pressure, temperature = bm_sensors()

    # Check validation
    print("put probe in the soil")
    answer = input("Is this data validated? If yes, press enter 'y' or 'n' to answer if the plant NEEDS water, otherwise press enter: ").strip().lower()
    if answer == 'y':
        validation = 'yes'
    elif answer == 'n':
        validation = 'no'
    else:
        validation = 'none'

    # Get sensor data
    q1h_lux = get_q1h_de_bilt("eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVkZTIzYzExYjIyYzQ5NDlhYzZjYjQ3ZmQxMDUwY2UxIiwiaCI6Im11cm11cjEyOCJ9")
    soilmoist = round(read_adc(0),2)

    print("soilmoist content = ", soilmoist)

    # Get model confidences
    model_conf, temp_conf, humi_conf, light_conf, soil_conf = process_data(
        [q1h_lux, humidity, temperature, soilmoist], return_all_conf=True
    )

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

    print(f"Plant health: {api_health}, Plant water problem: {api_water}, water deficiency: {api_water_deficiency}")
    flag = predict_flag(model_conf, api_health)

    print("soilmoist content2 = ", soilmoist)

    if not os.path.exists(raw_data_path):
        next_id = 1
    else:
        with open(processed_data_path, "r") as f:
            next_id = sum(1 for _ in f)

    if soilmoist > 20:
        soil_validation = 'B'
    else:
        soil_validation = 'A'


    # Build row for CSV
    row1 = {
        "image_name": f"{label}.jpg",
        "time": timestamp,
        "place": place,
        "temperature": temperature,
        "humidity": humidity,
        "sun_light": q1h_lux,
        "soil_moist": soilmoist,
        "API_health": api_health,
        "API_water": api_water,
        "API_water_def": api_water_deficiency,
        "validation": validation,
        "temp_conf": temp_conf,
        "humi_conf": humi_conf,
        "light_conf": light_conf,
        "soil_conf": soil_conf,
        "model_conf": model_conf,
        "final_tag": flag
    }

    row2 = {
        "ID": next_id,
        "image_name": f"{label}.jpg",
        "time": timestamp,
        "place": place,
        "temperature": temperature,
        "humidity": humidity,
        "sun_light": q1h_lux,
        "soil_moist": soilmoist,
        "API_health": api_health,
        "API_water": api_water,
        "API_water_def": api_water_deficiency,
        "validation": validation,
        "soil_validation": soil_validation
}

# Print much more, and get out of the programs itself

    if not testing:
        log_plant_data_processed(row1)
        log_plant_data_raw(row2)
        print(f"✅ Logged full data (with model confidences) to CSV.\n")
    else:
        print("Did not logg data, because in testing state")


# Main loop
try:
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.readline().strip()
            if key.lower() == "t":
                capture_and_log(place)
        time.sleep(0.05)
except KeyboardInterrupt:
    cam1.stop()
    print("\n[EXIT] Manual capture ended.")
