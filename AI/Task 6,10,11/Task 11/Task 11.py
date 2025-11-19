

import pandas as pd
from scipy.io import arff

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,)
from joblib import dump

def load_connect4_arff(path: str) -> pd.DataFrame:
    """Load Connect 4 ARFF using scipy.io.arff."""
    data, meta = arff.loadarff(path)
    df = pd.DataFrame(data)

    # Convert byte strings to normal strings
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda v: v.decode("utf-8") if isinstance(v, bytes) else v
            )
    return df



def prepare_features_and_labels(df: pd.DataFrame):
    """
    Convert board to integers and convert class to binary:
      1 = win (class == '2')
      0 = not win (class == '0' or '1')
    """

    # Convert board to integers
    X = df.drop(columns=["class"]).astype(int)

    # Binary win label
    y = (df["class"].astype(str) == "2").astype(int)

    return X, y


def train_model(X, y):
    """Train a tuned RandomForest model for better accuracy."""

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    model = RandomForestClassifier(
        n_estimators=1000,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,            
        class_weight=None,
    )
    model.fit(X_train, y_train)
 
    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy on test set: {acc:.4f}\n")

    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    return model, X_test.columns

def predict_position(model, feature_names):
    """Predict win for an empty board (example)."""

    example_board = [0] * len(feature_names)
    X_new = pd.DataFrame([example_board], columns=feature_names)

    prob_win = model.predict_proba(X_new)[0, 1]
    label = model.predict(X_new)[0]

    print("\nExample Prediction on Empty Board:")
    print("Predicted label:", label)
    print(f"Predicted win probability: {prob_win:.4f}")


def main():

    path = "connect-4.arff"  # make sure file is in same folder

    print("Loading data...")
    df = load_connect4_arff(path)
    print("Loaded:", df.shape, "rows")

    print("\nPreparing features and labels (binary classification)...")
    X, y = prepare_features_and_labels(df)
    print("Unique labels in y:", sorted(y.unique()))

    print("\nTraining model with improved accuracy...")
    model, feature_names = train_model(X, y)

    # Example prediction
    predict_position(model, feature_names)

    # Save the trained model
    dump(model, "connect4_win_model.joblib")
    print("\nModel saved as connect4_win_model.joblib")


if __name__ == "__main__":
    main()
