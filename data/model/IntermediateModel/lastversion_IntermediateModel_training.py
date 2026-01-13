"""
train_intermediate_models.py

This script loads a training dataset from the IntermediateModel directory and trains
multiple binary classification models to predict the 'validation' label based on:

Input features:
- Plant_health
- API_health

Target variable:
- validation (expected values: "y" or "n", mapped to 1 and 0)

Evaluation:
- Stratified 5-fold cross-validation
- Metrics: Accuracy, ROC AUC, confusion matrix, classification report,
  and summary metrics (precision/recall/F1 in macro and weighted averages)

Model persistence:
- Each model is fit on the full dataset after cross-validation and saved using joblib:
  - LR_model.pkl
  - RF_model.pkl
  - XGB_model.pkl
  """


import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import joblib

training_file = "data_training.csv"

# === Load and Prepare Data ===
df = pd.read_csv("/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/model/IntermediateModel/" + training_file)
features = ["Plant_health", "API_health"]
df = df[features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["y", "n"])]
X = df[features].astype(float)
y = df["validation"].str.lower().map({"y": 1, "n": 0})

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
    
    y_pred = cross_val_predict(model, X, y, cv=cv)
    y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')[:, 1]

    acc = accuracy_score(y, y_pred)
    roc_auc = roc_auc_score(y, y_proba)
    prec_macro = precision_score(y, y_pred, average='macro')
    recall_macro = recall_score(y, y_pred, average='macro')
    f1_macro = f1_score(y, y_pred, average='macro')
    prec_weighted = precision_score(y, y_pred, average='weighted')
    recall_weighted = recall_score(y, y_pred, average='weighted')
    f1_weighted = f1_score(y, y_pred, average='weighted')

    print(" Accuracy:", f"{acc:.4f}")
    print(" ROC AUC Score:", f"{roc_auc_score(y, y_proba):.4f}")
    print(" Confusion Matrix:\n", confusion_matrix(y, y_pred))
    print(" Classification Report:\n", classification_report(y, y_pred))

    print(" Summary Metrics:")
    print(f"  Precision (macro):   {prec_macro:.4f}")
    print(f"  Recall (macro):      {recall_macro:.4f}")
    print(f"  F1 Score (macro):    {f1_macro:.4f}")
    print(f"  Precision (weighted):{prec_weighted:.4f}")
    print(f"  Recall (weighted):   {recall_weighted:.4f}")
    print(f"  F1 Score (weighted): {f1_weighted:.4f}")

    # Fit on full data to get feature importances
    model.fit(X, y)
    print(" Feature Importances:")
    if name == "Logistic Regression":
        joblib.dump(model, "LR_model.pkl") 
        for feature, weight in zip(features, model.coef_[0]):
            print(f"  {feature}: {weight:.4f}")
    elif name == "Random Forest":
        joblib.dump(model, "RF_model.pkl")
        print("Random Forest model saved")
        for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
    else:
       joblib.dump(model, "XGB_model.pkl") 
       for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
