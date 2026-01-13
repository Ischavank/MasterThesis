import numpy as np
import joblib

def predict_flag(plant_health_confidence, api_health):
    """
    Uses trained Random Forest model to predict FLAG category.
    Inputs:
        - plant_health_confidence (float): result from `process_data`
        - api_health (float): external metric
    Returns:
        - FLAG (A, B, or C)
    """
    model_path = "/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/model/"
    model = joblib.load(model_path + "random_forest_model.pkl")
    label_encoder = joblib.load(model_path + "label_encoder.pkl")

    input_data = np.array([[api_health, plant_health_confidence]])
    print("model input data: ", input_data)
    pred = model.predict(input_data)
    label = label_encoder.inverse_transform(pred)

    print(f"🎯 Predicted FLAG: {label[0]}")
    return label[0]
