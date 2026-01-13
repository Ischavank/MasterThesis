import sys
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')
from model_usage import predict_flag


plant_health_conf = 90
api_health = 90

flag = predict_flag(plant_health_conf, api_health)

print(flag)
