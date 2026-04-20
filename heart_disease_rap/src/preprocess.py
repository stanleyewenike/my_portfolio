"""
preprocess.py
-------------
Build the sklearn preprocessing pipeline (imputation + encoding + scaling).

Stage 3. Returns a ColumnTransformer that can be fitted on training data only,
preventing train/test leakage.
"""
import logging
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

logger = logging.getLogger(__name__)


def build_numeric_pipeline() -> Pipeline:
    """Median imputation + standard scaling for numeric features."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])


def build_categorical_pipeline() -> Pipeline:
    """Mode imputation + one-hot encoding for categorical features."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", drop="first")),
    ])


def build_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    """
    Build a ColumnTransformer combining numeric and categorical pipelines.

    Embedded inside the model Pipeline to ensure preprocessing is refitted
    per CV fold, preventing any train/test contamination.
    """
    preprocessor = ColumnTransformer([
        ("num", build_numeric_pipeline(), numeric_features),
        ("cat", build_categorical_pipeline(), categorical_features),
    ])
    logger.info(
        f"Preprocessor built with {len(numeric_features)} numeric "
        f"and {len(categorical_features)} categorical features"
    )
    return preprocessor


def get_feature_names(fitted_preprocessor: ColumnTransformer,
                       numeric_features: list[str],
                       categorical_features: list[str]) -> list[str]:
    """Recover feature names after one-hot encoding, for interpretation."""
    ohe = fitted_preprocessor.named_transformers_["cat"].named_steps["encode"]
    cat_names = ohe.get_feature_names_out(categorical_features).tolist()
    return numeric_features + cat_names
