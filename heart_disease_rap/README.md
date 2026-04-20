# Heart Disease Predictive Model

A reproducible logistic regression prototype for predicting heart disease in patients presenting with chest pain. April 2026.

**Headline results:** 5-fold cross-validated ROC-AUC of 0.89; hold-out test ROC-AUC of 0.92; recall of 0.90 on 184 held-out patients.


---

## Why this structure

The pipeline is deliberately modular. Each stage is a single-purpose module that can be tested, reused, swapped, or inspected independently. A single orchestrator (`main.py`) wires them together. Configuration lives in `config.yaml`, not in source code, so re-running the pipeline on different data or parameters requires no edits to Python files.

This follows the UK Government Analytical Community's Reproducible Analytical Pipeline (RAP) principles. See `RAP.md` for the full compliance notes.

---

## Project structure

```
heart_disease_rap/
├── config.yaml              # All tunable parameters
├── main.py                  # Orchestrator (run this)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── RAP.md                   # RAP compliance notes
├── data/
│   └── raw/
│       └── heart_disease_uci.csv
├── src/
│   ├── __init__.py
│   ├── config.py            # Loads config.yaml
│   ├── data_loader.py       # Stage 1: load + data quality
│   ├── eda.py               # Stage 2: exploratory analysis
│   ├── preprocess.py        # Stage 3: sklearn preprocessor
│   ├── train.py             # Stage 4-6: model + CV + fit
│   └── evaluate.py          # Stage 7: metrics + plots
├── tests/
│   └── test_pipeline.py     # Sanity checks
└── outputs/                 # Generated on each run
    ├── 1_missingness.png
    ├── 2_prevalence_by_study.png
    ├── 3_roc_curve.png
    ├── 4_feature_importance.png
    ├── feature_coefficients.csv
    ├── heart_disease_model.pkl
    └── run_summary.json
```

---

## Quick start

### 1. Prerequisites

- Python 3.10 or newer
- Pip

### 2. Clone and set up

```bash
# Clone the repository
git clone <repo-url> heart_disease_rap
cd heart_disease_rap

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python main.py
```

Expected runtime: approximately 5 seconds. On completion, all artifacts are written to `outputs/`.

### 4. Run the tests

```bash
pytest tests/ -v
```

All four tests should pass, including a smoke test that reruns the full pipeline and asserts AUC above 0.7.

---

## Pipeline stages

| Stage | Module | Purpose |
|---|---|---|
| 1 | `data_loader.py` | Load raw CSV, recode physiologically impossible zeros, derive binary target |
| 2 | `eda.py` | Profile missingness, compute prevalence by study, save diagnostic plots |
| 3 | `preprocess.py` | Build sklearn ColumnTransformer (median + mode imputation, standard scaling, one-hot encoding) |
| 4 | `train.py` | Assemble model Pipeline (preprocessor + logistic regression) |
| 5 | `train.py` | Stratified 5-fold cross-validation on training set |
| 6 | `train.py` | Fit final model on full training set |
| 7 | `evaluate.py` | Score on hold-out test set; save ROC curve and feature importance |
| 8 | `main.py` | Persist model (`.pkl`), coefficients (`.csv`), and run summary (`.json`) |

---

## Configuration

All tunable parameters live in `config.yaml`. To change seed, switch features, or swap model hyperparameters, edit the YAML. No source code changes required.

```yaml
random:
  seed: 42

split:
  test_size: 0.2
  cv_folds: 5

features:
  drop_high_missing: [ca, thal]
  numeric: [age, trestbps, chol, thalch, oldpeak]
  categorical: [sex, dataset, cp, fbs, restecg, exang, slope]

model:
  params:
    max_iter: 2000
    C: 1.0
```

---

## Key design decisions

1. **Logistic regression** over tree ensembles. Interpretable coefficients are essential in a clinical context; L2 regularisation handles mild multicollinearity.
2. **Drop `ca` and `thal`** (66% and 53% missing). Imputation above 50% missingness introduces more noise than signal; the missingness pattern also correlates with study site (likely MNAR).
3. **Include `dataset` as a feature.** The four source studies show disease prevalence varying from 36% (Hungary) to 94% (Switzerland). Including study site as a covariate lets the clinical coefficients be estimated conditional on site, mitigating confounding.
4. **Recode `trestbps = 0` and `chol = 0` as missing.** Both are physiologically impossible and almost certainly sentinel values for not-measured.
5. **Embedded preprocessing.** The sklearn Pipeline wraps the imputer, scaler, and model together, so cross-validation refits preprocessing per fold and prevents train/test leakage.
6. **Prioritise recall over precision.** Missed diagnoses carry greater clinical risk than false alarms in a screening context.

---

## Reproducing results

The pipeline is deterministic. With the default seed (`42`), every run will produce identical metrics:

| Metric | Value |
|---|---|
| 5-fold CV ROC-AUC | 0.890 (+/- 0.019) |
| Test ROC-AUC | 0.918 |
| Test Recall | 0.902 |
| Test Precision | 0.829 |

---

## Data source

Heart Disease dataset, pooled from four research studies (Cleveland, Hungarian, Swiss, VA Long Beach). Provided with the technical assessment. 

## Disclaimer

Not representative of contemporary UK NHS populations; any real-world deployment would require external validation.

---

## License

Internal use only — NHSE technical assessment, April 2026.

## Author

Stanley Francis Ewenike
