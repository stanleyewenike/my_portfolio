"""
test_pipeline.py
----------------
Sanity tests for the pipeline. Keeps scope tight per the RAP principle
of 'minimal tests > no tests'.

Run with: pytest tests/
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import fix_impossible_values, derive_target
from src.preprocess import build_preprocessor


def test_fix_impossible_values_converts_zeros_to_nan():
    """Zero values in specified columns must be recoded as NaN."""
    df = pd.DataFrame({"trestbps": [120, 0, 140], "chol": [200, 0, 180]})
    result = fix_impossible_values(df, ["trestbps", "chol"])
    assert result["trestbps"].isna().sum() == 1
    assert result["chol"].isna().sum() == 1
    assert result.loc[0, "trestbps"] == 120  # untouched


def test_derive_target_is_binary():
    """Target derived from 'num' field must be binary 0/1."""
    df = pd.DataFrame({"num": [0, 1, 2, 3, 4, 0]})
    result = derive_target(df)
    assert set(result["target"].unique()) == {0, 1}
    assert result["target"].sum() == 4  # four non-zero values


def test_preprocessor_builds_without_error():
    """Preprocessor should construct a ColumnTransformer with named transformers."""
    preprocessor = build_preprocessor(["age", "chol"], ["sex", "cp"])
    transformer_names = [t[0] for t in preprocessor.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names


def test_pipeline_end_to_end_runs():
    """Smoke test: main.py must run and produce an AUC above chance."""
    from main import main
    summary = main()
    assert summary["test_metrics"]["roc_auc"] > 0.7, "Model AUC suspiciously low"
    assert summary["n_train"] > summary["n_test"], "Train set should exceed test set"
