"""
main.py
-------
Orchestrator for the Heart Disease Prediction pipeline.

Runs the full end-to-end workflow in order:
    1. Load and prepare data
    2. Exploratory data analysis
    3. Split train/test
    4. Build preprocessor + model
    5. Cross-validate
    6. Fit final model
    7. Evaluate on hold-out
    8. Persist artifacts

Usage:
    python main.py

Reproducibility: controlled by random.seed in config.yaml.
"""
import json
import logging
import sys
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

# Set up path so 'src' is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import CONFIG
from src.data_loader import load_and_prepare
from src.eda import run_eda
from src.preprocess import build_preprocessor
from src.train import build_model, cross_validate, fit_final_model
from src.evaluate import compute_metrics, plot_roc, plot_feature_importance


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> dict:
    configure_logging()
    logger = logging.getLogger("main")
    logger.info("=" * 70)
    logger.info(f"STARTING: {CONFIG['project']['name']} v{CONFIG['project']['version']}")
    logger.info("=" * 70)

    seed = CONFIG["random"]["seed"]
    out_dir = CONFIG["paths"]["outputs"]

    # ---- Stage 1: Load + prepare ------------------------------------------
    logger.info(">>> Stage 1: Load and prepare data")
    df = load_and_prepare(
        path=CONFIG["paths"]["raw_data"],
        impossible_zero_cols=CONFIG["features"]["impossible_zeros"],
    )

    # ---- Stage 2: EDA ----------------------------------------------------
    logger.info(">>> Stage 2: Exploratory data analysis")
    eda_results = run_eda(df, out_dir)

    # ---- Stage 3: Feature selection + split ------------------------------
    logger.info(">>> Stage 3: Feature selection and train/test split")
    numeric = CONFIG["features"]["numeric"]
    categorical = CONFIG["features"]["categorical"]
    X = df[numeric + categorical]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG["split"]["test_size"],
        stratify=y,
        random_state=seed,
    )
    logger.info(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows")

    # ---- Stage 4: Build pipeline -----------------------------------------
    logger.info(">>> Stage 4: Build preprocessor and model")
    preprocessor = build_preprocessor(numeric, categorical)
    model = build_model(
        preprocessor=preprocessor,
        model_params=CONFIG["model"]["params"],
        random_state=seed,
    )

    # ---- Stage 5: Cross-validate -----------------------------------------
    logger.info(">>> Stage 5: Cross-validation")
    cv_scores = cross_validate(
        model, X_train, y_train,
        cv_folds=CONFIG["split"]["cv_folds"],
        random_state=seed,
    )

    # ---- Stage 6: Fit final model ----------------------------------------
    logger.info(">>> Stage 6: Fit final model on full training set")
    model = fit_final_model(model, X_train, y_train)

    # ---- Stage 7: Evaluate -----------------------------------------------
    logger.info(">>> Stage 7: Evaluate on hold-out test set")
    metrics = compute_metrics(model, X_test, y_test)
    plot_roc(model, X_test, y_test, out_dir / "3_roc_curve.png")
    coef_df = plot_feature_importance(
        model, numeric, categorical, out_dir / "4_feature_importance.png"
    )

    # ---- Stage 8: Persist ------------------------------------------------
    logger.info(">>> Stage 8: Persist artifacts")
    joblib.dump(model, out_dir / "heart_disease_model.pkl")
    coef_df.to_csv(out_dir / "feature_coefficients.csv", index=False)

    summary = {
        "project": CONFIG["project"],
        "seed": seed,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "cv_roc_auc_mean": float(cv_scores.mean()),
        "cv_roc_auc_std": float(cv_scores.std()),
        "test_metrics": metrics,
    }
    with open(out_dir / "run_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    logger.info("=" * 70)
    logger.info("RUN COMPLETE")
    logger.info(f"  CV ROC-AUC:    {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")
    logger.info(f"  Test ROC-AUC:  {metrics['roc_auc']:.3f}")
    logger.info(f"  Test Recall:   {metrics['recall']:.3f}")
    logger.info(f"  Artifacts in:  {out_dir}")
    logger.info("=" * 70)
    return summary


if __name__ == "__main__":
    main()
