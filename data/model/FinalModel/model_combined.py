import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# === Load and Prepare Data ===
df = pd.read_csv("../data_raw1.csv")

features = ["temperature", "humidity", "sun_light", "soil_moist"]
df = df[features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["yes", "no"])]
X = df[features].astype(float)
y = df["validation"].str.lower().map({"yes": 1, "no": 0})

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# === Model Definitions ===
models = {
    "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    "XGBoost": XGBClassifier(eval_metric='logloss')
}

# === Train and Evaluate Each Model ===
for name, model in models.items():
    print(f"\n{'='*20} {name} {'='*20}")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("✅ Accuracy:", accuracy_score(y_test, y_pred))
    print("📊 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("📈 Classification Report:\n", classification_report(y_test, y_pred))

    print("📌 Feature Importances:")
    if name == "Logistic Regression":
        for feature, weight in zip(features, model.coef_[0]):
            print(f"  {feature}: {weight:.4f}")
    else:
        for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
