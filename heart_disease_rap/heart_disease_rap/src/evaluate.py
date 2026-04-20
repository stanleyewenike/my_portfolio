"""
evaluate.py
-----------
Score the fitted model against the held-out test set; generate diagnostic plots.

Stage 5. Separated from training so the hold-out set is scored exactly once.
"""
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


def compute_metrics(model: Pipeline, X_test, y_test) -> dict:
    """Compute standard classification metrics on the hold-out test set."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "n_test": len(y_test),
    }
    logger.info(f"Test metrics: AUC={metrics['roc_auc']:.3f}, Recall={metrics['recall']:.3f}, "
                f"Precision={metrics['precision']:.3f}")
    logger.info(f"Classification report:\n{classification_report(y_test, y_pred, target_names=['No disease', 'Disease'])}")
    return metrics


def plot_roc(model: Pipeline, X_test, y_test, output_path: Path) -> None:
    """Plot ROC curve for the hold-out test set."""
    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc_val = roc_auc_score(y_test, y_proba)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(6, 5.5))
    ax.plot(fpr, tpr, color="#1976d2", lw=2.5, label=f"Logistic Regression (AUC = {auc_val:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1.5, linestyle="--", label="Random classifier")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate (Recall)")
    ax.set_title("ROC Curve - Hold-out Test Set")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    logger.info(f"ROC plot saved: {output_path}")


def plot_feature_importance(model: Pipeline, numeric_features: list[str],
                              categorical_features: list[str], output_path: Path,
                              top_n: int = 12) -> pd.DataFrame:
    """
    Plot top-N logistic regression coefficients as interpretable feature importance.
    Returns the full coefficient dataframe.
    """
    from src.preprocess import get_feature_names

    feature_names = get_feature_names(
        model.named_steps["prep"], numeric_features, categorical_features
    )
    coefs = model.named_steps["clf"].coef_[0]
    coef_df = pd.DataFrame({"feature": feature_names, "coef": coefs})
    coef_df["abs"] = coef_df["coef"].abs()
    plot_df = coef_df.sort_values("abs", ascending=True).tail(top_n)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))
    colours = ["#c62828" if c > 0 else "#1976d2" for c in plot_df["coef"]]
    ax.barh(plot_df["feature"], plot_df["coef"], color=colours)
    ax.set_xlabel("Standardised Coefficient (log-odds)")
    ax.set_title(f"Top {top_n} Predictors - Logistic Regression\n(red = increases risk, blue = protective)")
    ax.axvline(0, color="black", lw=0.8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    logger.info(f"Feature importance plot saved: {output_path}")
    return coef_df
