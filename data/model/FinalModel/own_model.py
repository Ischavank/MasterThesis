import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("../data_raw1.csv")
features = ["temperature", "humidity", "sun_light", "soil_moist"]
df = df[features + ["validation"]].dropna()
df = df[df["validation"].str.lower().isin(["yes", "no"])]
df["validation"] = df["validation"].str.lower().map({"yes": 1, "no": 0})

X = df[features].values
y = df["validation"].values

def gini(y):
    classes, counts = np.unique(y, return_counts=True)
    probs = counts / counts.sum()
    return 1 - np.sum(probs ** 2)

def best_split(X, y):
    best_feature, best_threshold, best_gini = None, None, float('inf')
    
    for feature_index in range(X.shape[1]):
        values = np.unique(X[:, feature_index])
        for threshold in values:
            left_mask = X[:, feature_index] <= threshold
            right_mask = ~left_mask

            if len(y[left_mask]) == 0 or len(y[right_mask]) == 0:
                continue

            gini_left = gini(y[left_mask])
            gini_right = gini(y[right_mask])
            weighted_gini = (len(y[left_mask]) * gini_left + len(y[right_mask]) * gini_right) / len(y)

            if weighted_gini < best_gini:
                best_gini = weighted_gini
                best_feature = feature_index
                best_threshold = threshold

    return best_feature, best_threshold

class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, *, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # only used in leaves

def build_tree(X, y, depth=0, max_depth=5):
    if len(set(y)) == 1 or depth >= max_depth:
        # Leaf node: return most common class
        value = np.bincount(y).argmax()
        return Node(value=value)

    feature, threshold = best_split(X, y)
    if feature is None:
        value = np.bincount(y).argmax()
        return Node(value=value)

    left_mask = X[:, feature] <= threshold
    right_mask = ~left_mask

    left = build_tree(X[left_mask], y[left_mask], depth + 1, max_depth)
    right = build_tree(X[right_mask], y[right_mask], depth + 1, max_depth)

    return Node(feature=feature, threshold=threshold, left=left, right=right)

def predict_one(node, x):
    while node.value is None:
        if x[node.feature] <= node.threshold:
            node = node.left
        else:
            node = node.right
    return node.value

def predict(tree, X):
    return np.array([predict_one(tree, x) for x in X])

# Train
tree = build_tree(X, y, max_depth=4)

# Predict
y_pred = predict(tree, X)

# Evaluate
from sklearn.metrics import classification_report, accuracy_score
print("Accuracy:", accuracy_score(y, y_pred))
print(classification_report(y, y_pred))

