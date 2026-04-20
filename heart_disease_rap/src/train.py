"""
train.py
--------
Train the logistic regression model inside a full sklearn Pipeline.

Stage 4. Performs stratified CV, fits final model, returns artifacts.
"""
import logging
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.compose import ColumnTransformer

logger = logging.getLogger(__name__)


def build_model(preprocessor: ColumnTransformer, model_params: dict, random_state: int) -> Pipeline:
    """
    Assemble full pipeline: preprocessor -> classifier.

    Using logistic regression because:
    - Interpretable coefficients (clinical acceptance)
    - Appropriate baseline for a prototype
    - Robust given N=736 training rows
    - L2 regularisation handles mild multicollinearity
    """
    classifier = LogisticRegression(random_state=random_state, **model_params)
    model = Pipeline([
        ("prep", preprocessor),
        ("clf", classifier),
    ])
    logger.info(f"Model built: LogisticRegression with params {model_params}")
    return model


def cross_validate(model: Pipeline, X_train, y_train, cv_folds: int, random_state: int) -> np.ndarray:
    """
    Run stratified k-fold cross-validation, scoring by ROC-AUC.

    Stratification preserves the 55/45 target balance in every fold.
    CV is performed on training data only; the hold-out test set remains untouched.
    """
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
    logger.info(f"{cv_folds}-fold CV ROC-AUC: {scores.mean():.3f} +/- {scores.std():.3f}")
    logger.info(f"Fold scores: {[f'{s:.3f}' for s in scores]}")
    return scores


def fit_final_model(model: Pipeline, X_train, y_train) -> Pipeline:
    """Fit the pipeline on the full training set."""
    model.fit(X_train, y_train)
    logger.info(f"Final model fitted on {len(X_train)} rows")
    return model
