"""
lastversion_ModifySensoryData.py

This script implements a plant-knowledge (rule-based) transformation that maps
environmental sensor values to confidence scores (0–100). The scores reflect how
close the measured values are to plant-specific target ranges. A weighted average
is used to compute an overall "Plant_health" score.

Purpose in the IntermediateModel workflow:
- Soil moisture is collected separately and combined with environmental readings.
- After data collection, this script converts sensor readings into comparable scores.
- The resulting scores are saved to a new CSV for downstream machine learning steps.

Outputs:
- Plant_health (weighted mean confidence)
- Individual confidence scores for temperature, humidity, light, and soil moisture
"""


import csv
from datetime import datetime
import numpy as np

# === Your original functions ===

output_f = "test3.csv"

plant_settings = {
    'light_tag':       {'min': 3500, 'ideal': 40000, 'max': 130000},
    'humidity_tag':    {'min': 30,   'ideal': 60,    'max': 70},
    'temperature_tag': {'min': 10,   'ideal': 22,    'max': 32},
    'soilmoist_tag':   {'min': 20,   'ideal': 55,    'max': 65}
}

sigmoid_params = {
    'light_tag':       {'k': 0.1, 's': 15},
    'temperature_tag': {'k': 0.7, 's': 2},
    'humidity_tag':    {'k': 0.3, 's': 8},
    'soilmoist_tag':   {'k': 0.3, 's': 8}
}

def sigmoid_confidence(x, tag):
    settings = plant_settings[tag]
    params = sigmoid_params[tag]
    k = params['k']
    s = params['s']

    if tag == 'light_tag':
        percent = 100 * (x - settings['min']) / (settings['max'] - settings['min'])
        distance = 100 - percent
        confidence = 100 / (1 + np.exp(-k * (distance - s)))
    elif tag == 'temperature_tag':
        distance = settings['max'] - x
        confidence = 100 / (1 + np.exp(-k * (distance - s)))
    elif tag == 'humidity_tag' or tag == 'soilmoist_tag':
        distance = x - settings['min']
        confidence = 100 / (1 + np.exp(-k * (distance - s)))
    else:
        confidence = 100
    return round(confidence, 2)

def process_data(data_list, return_all_conf=False):
    qh, humidity, temperature, soilmoist = data_list
    hour = datetime.now().hour

    light_conf = sigmoid_confidence(qh, 'light_tag')
    humidity_conf = sigmoid_confidence(humidity, 'humidity_tag')
    temp_conf = sigmoid_confidence(temperature, 'temperature_tag')
    soilmoist_conf = sigmoid_confidence(soilmoist, 'soilmoist_tag')

    confidences = {
        'light_tag': light_conf,
        'humidity_tag': humidity_conf,
        'temperature_tag': temp_conf,
        'soilmoist_tag': soilmoist_conf
    }

    confidence_weights_day = {
        'light_tag': 0.22,
        'humidity_tag': 0.07,
        'temperature_tag': 0.11,
        'soilmoist_tag': 0.60
    }

    confidence_weights_night = {
        'light_tag' : 0.00,
        'humidity_tag': 0.32,
        'temperature_tag': 0.37,
        'soilmoist_tag': 0.31
    }

    weights = confidence_weights_day if 5 <= hour < 20 else confidence_weights_night

    weighted_total = sum(confidences[tag] * weights[tag] for tag in confidences)
    mean_confidence = round(weighted_total, 2)

    if return_all_conf:
        return mean_confidence, temp_conf, humidity_conf, light_conf, soilmoist_conf
    else:
        return mean_confidence

# === CSV Processing Code ===

input_file = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/test1.csv"
output_file = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/" + output_f

with open(input_file, newline='') as csvfile_in, open(output_file, 'w', newline='') as csvfile_out:
    reader = csv.DictReader(csvfile_in)
    fieldnames = reader.fieldnames + [
        'Plant_health',
        'temp_confidence',
        'humidity_confidence',
        'light_confidence',
        'soilmoist_confidence'
    ]
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            temperature = float(row['temperature'])
            humidity = float(row['humidity'])
            sunlight = float(row['sun_light'])
            soilmoist = float(row['soil_moist'])

            mean_conf, temp_conf, hum_conf, light_conf, soil_conf = process_data(
                [sunlight, humidity, temperature, soilmoist], return_all_conf=True
            )

            row.update({
                'Plant_health': mean_conf,
                'temp_confidence': temp_conf,
                'humidity_confidence': hum_conf,
                'light_confidence': light_conf,
                'soilmoist_confidence': soil_conf
            })

        except Exception as e:
            print(f"❌ Skipping row due to error: {e}")
            continue

        writer.writerow(row)

print(f"✅ CSV processed. Output written to {output_file}")
