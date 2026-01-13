import numpy as np
from datetime import datetime

# Ideal sensor settings per tag
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

    # Light: reverse sigmoid based on % away from max
    if tag == 'light_tag':
        percent = 100 * (x - settings['min']) / (settings['max'] - settings['min'])
        distance = 100 - percent
        confidence = 100 / (1 + np.exp(-k * (distance - s)))

    # Temperature: reverse sigmoid from max
    elif tag == 'temperature_tag':
        distance = settings['max'] - x
        confidence = 100 / (1 + np.exp(-k * (distance - s)))

    # Humidity: forward sigmoid from min
    elif tag == 'humidity_tag':
        distance = x - settings['min']
        confidence = 100 / (1 + np.exp(-k * (distance - s)))

    # Soil Moisture: forward sigmoid from min
    elif tag == 'soilmoist_tag':
        distance = x - settings['min']
        confidence = 100 / (1 + np.exp(-k * (distance - s)))

    else:
        confidence = 100  # fallback default if tag not matched

    return round(confidence, 2)

def process_data(data_list, return_all_conf=False):
    """
    Expects list: [qh (sunlight), humidity, temperature, soilmoist]
    Computes and returns weighted plant health confidence (0–100).
    If return_all_conf=True, also returns individual confidences for each sensor.
    """
    qh, humidity, temperature, soilmoist = data_list
    hour = datetime.now().hour

    # Confidence scores per sensor
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

    # Weight per tag
    confidence_weights_day = {
        'light_tag': 0.35,
        'humidity_tag': 0.20,
        'temperature_tag': 0.25,
        'soilmoist_tag': 0.20
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

    print(f"✅ Confidences → Light: {light_conf}%, Humidity: {humidity_conf}%, "
          f"Temperature: {temp_conf}%, Soil Moisture: {soilmoist_conf}%")
    print(f"📈 Weighted Plant Health Confidence: {mean_confidence}%")

    if return_all_conf:
        return mean_confidence, temp_conf, humidity_conf, light_conf, soilmoist_conf
    else:
        return mean_confidence
