import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# === Load and Prepare Data ===
df = pd.read_csv("/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_raw1.csv")

features = ["API_health", "API_water", "API_water_def"]
df = df[features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["yes", "no"])]
X = df[features].astype(float)
y = df["validation"].str.lower().map({"yes": 1, "no": 0})

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# === Model Definitions ===
models = {
    "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    "XGBoost": XGBClassifier(eval_metric='logloss')
}

# === Store Accuracy Scores for Plot ===
accuracy_scores = {}

# === Train and Evaluate Each Model ===
for name, model in models.items():
    print(f"\n{'='*20} {name} {'='*20}")
    
    # Cross-validated predictions (labels)
    y_pred = cross_val_predict(model, X, y, cv=cv)
    y_prob = cross_val_predict(model, X, y, cv=cv, method='predict_proba')[:, 1]


    acc = accuracy_score(y, y_pred)
    auc = roc_auc_score(y, y_prob)
    accuracy_scores[name] = acc

    print(f" Accuracy: {acc:.4f}")
    print(f" ROC AUC Score: {auc:.4f}")
    print(" Confusion Matrix:\n", confusion_matrix(y, y_pred))
    print(" Classification Report:\n", classification_report(y, y_pred))

    model.fit(X, y)

    print(" Feature Importances:")
    if name == "Logistic Regression":
        for feature, weight in zip(features, model.coef_[0]):
            print(f"  {feature}: {weight:.4f}")
    else:
        for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")

# === Plot Accuracy Comparison ===
plt.figure(figsize=(8, 5))
model_names = list(accuracy_scores.keys())
accuracies = list(accuracy_scores.values())

plt.bar(model_names, accuracies)
plt.axhline(y=0.5, color='gray', linestyle='dotted', linewidth=1.5, label='Random Guess (50%)')

plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()
