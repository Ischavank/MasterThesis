import requests
import base64
import json

def assess_plant_health(image_path, api_key, latitude=None, longitude=None):
    """
    Sends a plant image to Plant.ID health assessment endpoint and returns health data.
    """
    try:
        # Encode image
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        # Prepare request
        payload = {
            "images": [base64_image],
            "latitude": latitude,
            "longitude": longitude,
            "similar_images": False,
            "health": "auto"
        }

        headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key
        }

        # Send POST request
        response = requests.post(
            "https://api.plant.id/v2/health_assessment",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        data = response.json()

        # Data extraction part
        is_healthy_prob = data.get("is_healthy_probability", None)

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

    except Exception as e:
        print(f"❌ Error during plant health assessment: {e}")
        return None
