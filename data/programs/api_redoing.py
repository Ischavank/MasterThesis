import csv
import os
import requests
import base64
import json

# === CONFIG ===
csv_file_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_raw1.csv"     # Your CSV file
image_column = "image_name"                 # Column that contains the image file name
image_directory = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/photos4"                  # Directory where the images are stored
api_key = "WhAoSeotJiiMPdHqUHwzG3C0xwakXtIvqhPWl07YsajreJvwCI"          # Your Plant.ID API key
output_csv_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_raw2.csv"        # Where to save the updated CSV
start_index = 300                             # Start from this row (0-based, not counting header)
batch_size = 32                            # Number of rows to process per run

# === Plant.ID API Call ===
def assess_plant_health(image_path, api_key, latitude=None, longitude=None):
    try:
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

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

        response = requests.post(
            "https://api.plant.id/v2/health_assessment",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None

# === Extract key fields from API response ===
def extract_water_health_metrics(data):
    health_data = data.get("health_assessment", {})
    is_healthy_prob = health_data.get("is_healthy_probability", None)

    water_related_prob = None
    water_related_redundant = None
    water_deficiency_prob = None
    water_deficiency_redundant = None


    for disease in health_data.get("diseases", []):
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

# === Main Processing ===
updated_rows = []
with open(csv_file_path, newline='') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    rows = list(reader)

    for i, row in enumerate(rows):
        if i < start_index:
            updated_rows.append(row)
            continue
        if i >= start_index + batch_size:
            updated_rows.append(row)
            continue

        image_filename = row[image_column]
        image_path = os.path.join(image_directory, image_filename)

        if not os.path.exists(image_path):
            print(f"⚠️ Image not found: {image_path}")
            row["api_health"] = ""
            row["api_water"] = ""
            row["api_water_deficiency"] = ""
            updated_rows.append(row)
            continue

        print(f"📸 Processing row {i}: {image_filename}")
        data = assess_plant_health(image_path, api_key)

        if data is None:
            row["api_health"] = ""
            row["api_water"] = ""
            row["api_water_deficiency"] = ""
            print(f"⚠️  No data returned from API for {image_filename}.")
        else:
            metrics = extract_water_health_metrics(data)

            api_health = round((metrics["is_healthy_probability"] or 0) * 100, 1)
            api_water = round((metrics["water_related_issue"]["probability"] or 0) * 100, 1)
            api_water_deficiency = round((metrics["water_deficiency"]["probability"] or 0) * 100, 1)

            row["API_health"] = api_health
            row["API_water"] = api_water
            row["API_water_def"] = api_water_deficiency

            print(f"✅ Row {i} | {image_filename}")
            print(f"   → Health: {api_health}%, Water Issue: {api_water}%, Water Deficiency: {api_water_deficiency}%")

        updated_rows.append(row)

# === Save output ===
with open(csv_file_path, mode="w", newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

print(f"✅ Processed rows {start_index} to {start_index + batch_size - 1}. Results saved to {output_csv_path}.")
