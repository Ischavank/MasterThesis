import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold, cross_val_score


# === Load and Prepare Data ===
df = pd.read_csv("../data_raw1.csv")

all_features = ["temperature", "humidity", "sun_light", "soil_moist", "API_health"]
df = df[all_features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["yes", "no"])]

X_full = df[all_features].astype(float)
y = df["validation"].str.lower().map({"yes": 1, "no": 0})

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


# === Function to score a model using selected features ===
def score_model(features_to_use):
    X_sub = X_full[features_to_use]    # same X_full, y you defined
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        random_state=42
    )
    scores = cross_val_score(
        model,
        X_sub,
        y,
        cv=cv,               # <-- use the shuffled CV here
        scoring='accuracy'
    )
    return np.mean(scores)
# === Try different feature combinations ===
print("\n✅ All features:")
print("Accuracy:", score_model(all_features))

print("\n⛔ Without temperature:")
print("Accuracy:", score_model(["humidity", "sun_light", "soil_moist", "API_health"]))

print("\n⛔ Without soil_moist:")
print("Accuracy:", score_model(["temperature", "humidity", "sun_light", "API_health"]))

print("\n⛔ Without sunlight:")
print("Accuracy:", score_model(["temperature", "humidity", "soil_moist", "API_health"]))

print("\n⛔ Without API_health:")
print("Accuracy:", score_model(["temperature", "humidity", "sun_light", "soil_moist"]))

print("\n⛔ Only soil_moist:")
print("Accuracy:", score_model(["soil_moist"]))
