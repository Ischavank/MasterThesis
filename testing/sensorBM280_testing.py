import sys
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')
from sensorBM280 import bm_sensors

humidity, pressure, temperature = bm_sensors()

print(f"humidity: {humidity} and temperature: {temperature}")
