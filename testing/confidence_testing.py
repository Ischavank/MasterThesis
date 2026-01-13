import sys
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')

from confidence import process_data

qg = 10000
humidity = 80
temperature = 24
soilmoist = 20

plant_health_conf = process_data([qg, humidity, temperature, soilmoist], return_all_conf=True)

print(plant_health_conf)
