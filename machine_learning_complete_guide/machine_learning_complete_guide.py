"""Complete Machine Learning guide and reusable demonstration pipeline.

This file is intentionally educational: it walks through the end-to-end ML
workflow from problem definition and data preparation to training, evaluation,
comparison, tuning, interpretation, persistence, and inference.
"""
from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def load_data():
    dataset = load_breast_cancer(as_frame=True)
    X, y = dataset.data, dataset.target
    print(f"Dataset shape: {X.shape}")
    print(f"Features: {X.shape[1]}")
    print(f"Classes: {list(dataset.target_names)}")
    return X, y


def build_models():
    return {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000, random_state=42)),
        ]),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }


def evaluate(name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    print(f"\n=== {name} ===")
    print(f"Accuracy: {accuracy_score(y_test, pred):.4f}")
    print(f"ROC-AUC:  {roc_auc_score(y_test, proba):.4f}")
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))
    print(classification_report(y_test, pred, target_names=["class_0", "class_1"]))
    return model


def tune_random_forest(X_train, y_train):
    grid = {
        "n_estimators": [200, 400],
        "max_depth": [None, 8, 15],
        "min_samples_split": [2, 5],
        "max_features": ["sqrt", "log2"],
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        grid, scoring="roc_auc", cv=cv, n_jobs=-1, verbose=0,
    )
    search.fit(X_train, y_train)
    print("\nBest parameters:", search.best_params_)
    print(f"Best CV ROC-AUC: {search.best_score_:.4f}")
    return search.best_estimator_


def main():
    print("=" * 72)
    print("COMPLETE MACHINE LEARNING WORKFLOW")
    print("=" * 72)
    print("1. Problem definition -> 2. Data -> 3. EDA -> 4. Cleaning")
    print("5. Feature engineering -> 6. Split -> 7. Train -> 8. Evaluate")
    print("9. Cross-validation -> 10. Hyperparameter tuning -> 11. Save model")

    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    for name, model in build_models().items():
        evaluate(name, model, X_train, X_test, y_train, y_test)

    best_model = tune_random_forest(X_train, y_train)
    evaluate("Tuned Random Forest", best_model, X_train, X_test, y_train, y_test)

    output = Path(__file__).resolve().parent / "best_model.joblib"
    joblib.dump(best_model, output)
    print(f"\nSaved model: {output}")

    sample = X_test.iloc[[0]]
    prediction = best_model.predict(sample)[0]
    probability = best_model.predict_proba(sample).max()
    print(f"Example prediction: class={prediction}, confidence={probability:.2%}")


if __name__ == "__main__":
    main()
