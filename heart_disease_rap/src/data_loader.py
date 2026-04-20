"""
data_loader.py
--------------
Loads raw CSV, applies data quality fixes, derives binary target.

Stage 1 of the pipeline. Pure transformation: no model training, no plotting.
"""
import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


def load_raw(path: Path) -> pd.DataFrame:
    """Load the raw CSV file."""
    logger.info(f"Loading raw data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")
    return df


def fix_impossible_values(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Recode physiologically impossible zeros as NaN.

    trestbps = 0 (resting BP) is impossible (patient would be dead).
    chol = 0 (serum cholesterol) is almost certainly a not-measured sentinel.
    """
    df = df.copy()
    total_fixed = 0
    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column {col} not in dataframe; skipping")
            continue
        mask = df[col] == 0
        n_fixed = mask.sum()
        total_fixed += n_fixed
        df.loc[mask, col] = np.nan
        if n_fixed > 0:
            logger.info(f"Recoded {n_fixed} impossible zeros in {col} as NaN")
    logger.info(f"Total impossible values fixed: {total_fixed}")
    return df


def derive_target(df: pd.DataFrame, source_col: str = "num") -> pd.DataFrame:
    """
    Derive binary target from ordinal 'num' field.
    num > 0 indicates any presence of heart disease.
    """
    df = df.copy()
    df["target"] = (df[source_col] > 0).astype(int)
    logger.info(f"Target distribution: {df['target'].value_counts().to_dict()}")
    return df


def load_and_prepare(path: Path, impossible_zero_cols: list[str]) -> pd.DataFrame:
    """Full data loading pipeline: raw -> DQ fixes -> target derivation."""
    df = load_raw(path)
    df = fix_impossible_values(df, impossible_zero_cols)
    df = derive_target(df)
    return df
