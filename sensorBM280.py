import bme280
import smbus2
import time
import numpy as np

port = 1
address = 0x76 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

def bm_sensors():
    data = [[],[],[]] #humidity, pressure, temperature
    for i in range(5):
        bme280_data = bme280.sample(bus,address)
        data[0].append(bme280_data.humidity)
        data[1].append(bme280_data.pressure)
        data[2].append(bme280_data.temperature)
        time.sleep(1)
    print("humidity ",int(np.mean(data[0])),"  pressure ",int(np.mean(data[1])),"  temperature ",int(np.mean(data[2])))
    return round(np.mean(data[0]),2) , round(np.mean(data[1]),2) , round(np.mean(data[2]),2)
