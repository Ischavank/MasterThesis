import sys
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')
from weather_api import get_q1h_de_bilt

weather_api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVkZTIzYzExYjIyYzQ5NDlhYzZjYjQ3ZmQxMDUwY2UxIiwiaCI6Im11cm11cjEyOCJ9"
q1h_lux = get_q1h_de_bilt(weather_api_key)

print(q1h_lux)
