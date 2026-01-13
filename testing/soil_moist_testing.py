import sys
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')

from soil_moist import read_adc

data = read_adc(0)
print(data)
