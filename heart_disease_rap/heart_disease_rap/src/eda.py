"""
eda.py
------
Exploratory data analysis: profiling, missingness, heterogeneity checks.

Stage 2 of the pipeline. Produces summary statistics and diagnostic plots.
"""
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


def profile_missingness(df: pd.DataFrame) -> pd.Series:
    """Return % missingness per column, sorted descending."""
    missing_pct = (df.isna().sum() / len(df) * 100).round(1)
    missing_pct = missing_pct.sort_values(ascending=False)
    logger.info(f"Missingness profile:\n{missing_pct[missing_pct > 0]}")
    return missing_pct


def prevalence_by_study(df: pd.DataFrame, study_col: str = "dataset") -> pd.DataFrame:
    """Compute target prevalence by source study."""
    prev = df.groupby(study_col)["target"].agg(["mean", "count"]).round(3)
    logger.info(f"Prevalence by study:\n{prev}")
    return prev


def plot_missingness(df: pd.DataFrame, output_path: Path) -> None:
    """Bar chart of missingness by feature, colour-coded by severity."""
    sns.set_style("whitegrid")
    missing = df.drop(columns=["target"], errors="ignore").isna().mean().sort_values(ascending=False)
    colors = ["#d32f2f" if v > 0.5 else "#ff9800" if v > 0.3 else "#1976d2" for v in missing]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(missing.index, missing.values * 100, color=colors)
    ax.set_xlabel("% Missing")
    ax.set_title("Missingness by Feature (red=dropped, orange=imputed with caution, blue=low)")
    ax.axvline(50, color="red", linestyle="--", alpha=0.5, label="Drop threshold (50%)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    logger.info(f"Missingness plot saved: {output_path}")


def plot_prevalence_by_study(prev: pd.DataFrame, output_path: Path) -> None:
    """Bar chart of disease prevalence across source studies."""
    sns.set_style("whitegrid")
    prev_sorted = prev.sort_values("mean")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colours = ["#1976d2", "#42a5f5", "#ef6c00", "#c62828"]
    ax.bar(prev_sorted.index, prev_sorted["mean"], color=colours[: len(prev_sorted)])
    for i, (_, row) in enumerate(prev_sorted.iterrows()):
        ax.text(i, row["mean"] + 0.02, f"n={int(row['count'])}", ha="center", fontsize=10)
    ax.set_ylabel("Heart Disease Prevalence")
    ax.set_title("Disease Prevalence by Source Study")
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    logger.info(f"Prevalence plot saved: {output_path}")


def run_eda(df: pd.DataFrame, output_dir: Path) -> dict:
    """Run full EDA suite; return summary dict."""
    missing = profile_missingness(df)
    prev = prevalence_by_study(df)
    plot_missingness(df, output_dir / "1_missingness.png")
    plot_prevalence_by_study(prev, output_dir / "2_prevalence_by_study.png")
    return {"missing_pct": missing, "prevalence_by_study": prev}
