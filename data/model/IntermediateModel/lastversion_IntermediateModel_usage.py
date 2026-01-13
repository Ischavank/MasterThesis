"""
lastversion_IntermediateModel_usage.py

Offline evaluation script for pre-trained classification models.

This script loads previously trained models (stored as .pkl files), applies them to a
test dataset, and (optionally) computes evaluation metrics if ground truth labels
are available in the test file.

Models:
- Logistic Regression
- Random Forest
- XGBoost

Test data:
- Loaded from a CSV file
- Uses the same feature columns as during training

Outputs:
- Printed metrics (if 'validation' column exists)
- Optional CSV export with predictions (currently commented out)
"""

import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score
)

# === Filepaths for models ===
model_paths = {
    "Logistic Regression": "LR_model.pkl",
    "Random Forest": "RF_model.pkl",
    "XGBoost": "XGB_model.pkl"
}

# === Load test data ===
test_df_original = pd.read_csv("/home/ischavk/Master_Thesis_Ischa/Programs/Final_code/data/test2.csv")

# === Use same feature columns as during training ===
features = ["Plant_health", "API_health"]

# === Ground truth check ===
has_ground_truth = "validation" in test_df_original.columns

if has_ground_truth:
    y_true = test_df_original["validation"].str.lower().map({"yes": 1, "no": 0})

# === Evaluate each model ===
for name, path in model_paths.items():
    print(f"\n{'='*20} {name} Evaluation {'='*20}")
    
    model = joblib.load(path)
    
    # Copy test data so each model writes separately
    test_df = test_df_original.copy()
    X_test = test_df[features].astype(float)

    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Save predictions
    test_df["predicted_validation"] = y_pred
    test_df["predicted_confidence"] = y_proba
#    test_df.to_csv(f"test_with_predictions_{name.replace(' ', '_')}.csv", index=False)
#    print(f" Predictions saved to 'test_with_predictions_{name.replace(' ', '_')}.csv'")

    # Evaluation
    if has_ground_truth:
        print(" MODEL EVALUATION METRICS:")
        acc = accuracy_score(y_true, y_pred)
        auc = roc_auc_score(y_true, y_proba)
        f1_macro = f1_score(y_true, y_pred, average='macro')
        f1_weighted = f1_score(y_true, y_pred, average='weighted')

        print(f" Accuracy:          {acc:.4f}")
        print(f" ROC AUC Score:     {auc:.4f}")
        print(f" F1 Score (macro):   {f1_macro:.4f}")
        print(f" F1 Score (weighted):{f1_weighted:.4f}")
        print(" Confusion Matrix:\n", confusion_matrix(y_true, y_pred))
        print("CClassification Report:\n", classification_report(y_true, y_pred))
    else:
        print(" Column 'validation' not found in test file, skipping metrics.")
