"""
lastversion_FinalModel.py

Offline evaluation script for the "FinalModel" using greenhouse robot data.

This script trains and evaluates multiple binary classification models to predict
a validation label ("yes" / "no") based on environmental and soil-related features:

Input features:
- temperature
- humidity
- sun_light
- soil_moist

Target variable:
- validation (mapped to 1 for "yes", 0 for "no")

Evaluation method:
- Stratified K-Fold cross-validation (5 folds)
- Cross-validated predictions (class labels + probabilities)

Reported metrics:
- Accuracy
- ROC AUC
- Confusion matrix
- Full classification report
- Summary metrics (precision/recall/F1 in macro and weighted averages)

"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# === Load and Prepare Data ===
df = pd.read_csv("/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/data_raw1.csv")
features = ["temperature", "humidity", "sun_light", "soil_moist"]
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

# === Train and Evaluate Each Model ===
for name, model in models.items():
    print(f"\n{'='*20} {name} {'='*20}")
    
    # Get predictions
    y_pred = cross_val_predict(model, X, y, cv=cv)
    y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')[:, 1]  # Probability for class 1

    # Metrics
    acc = accuracy_score(y, y_pred)
    auc = roc_auc_score(y, y_proba)  # ROC AUC Score
    prec_macro = precision_score(y, y_pred, average='macro')
    recall_macro = recall_score(y, y_pred, average='macro')
    f1_macro = f1_score(y, y_pred, average='macro')
    prec_weighted = precision_score(y, y_pred, average='weighted')
    recall_weighted = recall_score(y, y_pred, average='weighted')
    f1_weighted = f1_score(y, y_pred, average='weighted')

    # Print metrics
    print(" Accuracy:", f"{acc:.4f}")
    print(" ROC AUC Score:", f"{auc:.4f}")
    print(" Confusion Matrix:\n", confusion_matrix(y, y_pred))
    print(" Classification Report:\n", classification_report(y, y_pred))

    print(" Summary Metrics:")
    print(f"  Precision (macro):   {prec_macro:.4f}")
    print(f"  Recall (macro):      {recall_macro:.4f}")
    print(f"  F1 Score (macro):    {f1_macro:.4f}")
    print(f"  Precision (weighted):{prec_weighted:.4f}")
    print(f"  Recall (weighted):   {recall_weighted:.4f}")
    print(f"  F1 Score (weighted): {f1_weighted:.4f}")

    # === Feature Importances ===
    model.fit(X, y)
    print(" Feature Importances:")
    if name == "Logistic Regression":
        for feature, weight in zip(features, model.coef_[0]):
            print(f"  {feature}: {weight:.4f}")
    else:
        for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
