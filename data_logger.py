import csv
import os

file_pro = "data/data_processed1.csv"
file_raw = "data/data_raw1.csv"

PROCESSED_HEADERS = ["image_name", "time", "place","temperature", "humidity", "sun_light", "soil_moist",
    "API_health", "API_water", "API_water_def", "validation", "temp_conf", "humi_conf", "light_conf", "soil_conf",
    "model_conf", "final_tag"
]

RAW_HEADERS = ["ID", "image_name", "time", "place","temperature", "humidity", "sun_light", "soil_moist",
    "API_health", "API_water", "API_water_def", "validation", "soil_validation"
]

def log_plant_data_processed(row_data: dict):
    with open(file_pro, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PROCESSED_HEADERS)
        writer.writerow(row_data)

def log_plant_data_raw(row_data: dict):
    with open(file_raw, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADERS)
        writer.writerow(row_data)

