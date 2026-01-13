from PIL import Image
import sys
import os
sys.path.append('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code')
from plant_api import assess_plant_health

files = os.listdir('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos3')

#image_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos3/" + files[10]
image_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos5/1.jpg"
api_key = "93j1F4tg9Vq1QIKKo9JoY6hEiT2JGZxV8nMplZvIJYVeqqWDAh"
api_key2 = "ko0YBQoTxHcbXSWUy531LjuzA3Swg8auupGnGRXMUbxLPgLuEL"
#health_score = assess_plant_health(image_path, api_key, latitude=None, longitude=None)

# If testing True, use real data, if false: Fake data
testing = True

def extract_health_metrics(data):
    is_healthy_prob = data.get("is_healthy_probability", None)

    print(data)

    water_related_prob = None
    water_related_redundant = None

    water_deficiency_prob = None
    water_deficiency_redundant = None

    for disease in data.get("diseases", []):
        name = disease.get("name", "").lower()
        prob = disease.get("probability", None)
        redundant = disease.get("redundant", None)

        if name == "water-related issue":
            water_related_prob = prob
            water_related_redundant = redundant

        elif name == "water deficiency":
            water_deficiency_prob = prob
            water_deficiency_redundant = redundant

    return {
        "is_healthy_probability": is_healthy_prob,
        "water_related_issue": {
            "probability": water_related_prob,
            "redundant": water_related_redundant
        },
        "water_deficiency": {
            "probability": water_deficiency_prob,
            "redundant": water_deficiency_redundant
        }
    }

if testing == True:
    data = assess_plant_health(image_path, api_key2, latitude=None, longitude=None)
    print("data", data)

    healthy_prob = data['is_healthy_probability']
    water_related_prob = data['diseases'][1]['probability']
    water_deficiency_prob = data['diseases'][2]['probability']

elif testing == False:
    data = {'is_healthy': True, 'is_healthy_probability': 0.7307547628879547, 'diseases': [{'name': 'Abiotic', 'probability': 0.374, 'redundant': True, 'entity_id': 456, 'disease_details': {'local_name': 'abiotic', 'language': 'en'}}, {'name': 'water-related issue', 'probability': 0.258, 'redundant': True, 'entity_id': 941, 'disease_details': {'local_name': 'water-related issue', 'language': 'en'}}, {'name': 'water deficiency', 'probability': 0.1866, 'entity_id': 907, 'disease_details': {'local_name': 'water deficiency', 'language': 'en'}}, {'name': 'light-related issue', 'probability': 0.173, 'redundant': True, 'entity_id': 942, 'disease_details': {'local_name': 'light-related issue', 'language': 'en'}}, {'name': 'water excess or uneven watering', 'probability': 0.1623, 'entity_id': 899, 'disease_details': {'local_name': 'water excess or uneven watering', 'language': 'en'}}, {'name': 'lack of light', 'probability': 0.1484, 'entity_id': 909, 'disease_details': {'local_name': 'lack of light', 'language': 'en'}}, {'name': 'nutrient deficiency', 'probability': 0.1022, 'entity_id': 801, 'disease_details': {'local_name': 'nutrient deficiency', 'language': 'en'}}, {'name': 'nutrient-related issue', 'probability': 0.0951, 'redundant': True, 'entity_id': 943, 'disease_details': {'local_name': 'nutrient-related issue', 'language': 'en'}}, {'name': 'mechanical damage', 'probability': 0.0756, 'entity_id': 793, 'disease_details': {'local_name': 'mechanical damage', 'language': 'en'}}, {'name': 'light or heat source damage', 'probability': 0.0521, 'entity_id': 900, 'disease_details': {'local_name': 'light or heat source damage', 'language': 'en'}}]}

    healthy_prob = data['is_healthy_probability']
    water_related_prob = data['diseases'][1]['probability']
    water_deficiency_prob = data['diseases'][2]['probability']

print("data",data)
print("Healthy Probability:", healthy_prob)
print("Water-related issue Probability:", water_related_prob)
print("Water deficiency Probability:", water_deficiency_prob)

files = os.listdir('/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos3')
print(files[1])

print(extract_health_metrics(data))


