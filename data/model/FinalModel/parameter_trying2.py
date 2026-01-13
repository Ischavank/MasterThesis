import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score

# === Load and Prepare Data ===
df = pd.read_csv("../data_raw1.csv")

all_features = ["temperature", "humidity", "sun_light", "soil_moist", "API_health"]
df = df[all_features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["yes", "no"])]

X_full = df[all_features].astype(float)
y = df["validation"].str.lower().map({"yes": 1, "no": 0})

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# === Function to score a model and print feature importances ===
def score_model(features_to_use):
    X_sub = X_full[features_to_use]
    
    importances_list = []
    accuracy_list = []

    for train_idx, test_idx in cv.split(X_sub, y):
        X_train, X_test = X_sub.iloc[train_idx], X_sub.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy_list.append(accuracy_score(y_test, y_pred))
        importances_list.append(model.feature_importances_)

    avg_accuracy = np.mean(accuracy_list)
    avg_importances = np.mean(importances_list, axis=0)

    print(f"Accuracy: {avg_accuracy:.3f}")
    print("Feature importances:")
    for feat, imp in zip(features_to_use, avg_importances):
        print(f"  {feat:15s}: {imp:.4f}")
    print("-" * 40)

# === Try different feature combinations ===
#print("\n✅ All features:")
#score_model(all_features)

print("\n⛔ Without temperature:")
#score_model(["humidity", "sun_light", "soil_moist", "API_health"])

print("\n⛔ Without soil_moist:")
#score_model(["temperature", "humidity", "sun_light", "API_health"])

print("\n⛔ Without sunlight:")
#score_model(["temperature", "humidity", "soil_moist", "API_health"])

print("\n⛔ Without API_health:")
score_model(["temperature", "humidity", "sun_light", "soil_moist"])

print("\n⛔ Only soil_moist:")
#score_model(["soil_moist"])
