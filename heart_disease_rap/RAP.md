# RAP Compliance — Reproducible Analytical Pipeline

This project follows the UK Government Analytical Community's **Reproducible Analytical Pipeline (RAP)** principles, as set out by the Office for National Statistics.

RAP is neither a tool or a framework; it can be referred to as a set of working principles that collectively ensure analysis is trustworthy, repeatable, and auditable. Each principle below is mapped to concrete evidence in this repository

---

## 1. Version controlled

**Principle:** All code, configuration, and documentation lives in version control. Every change is traceable.

**Evidence:**

- All source code sits under `src/`, tracked in Git.
- All tunable parameters sit in `config.yaml`, tracked in Git. No hard-coded constants in source code.
- `run_summary.json` captures the full configuration, seed, and metrics for every pipeline run, providing a durable audit record.
- `.gitignore` excludes `outputs/` from version control (artifacts are reproducible from source, so they should not pollute history).

---

## 2. Modular and reusable

**Principle:** Analysis is decomposed into small, single-purpose units that can be tested, swapped, and reused independently.

**Evidence:** The pipeline is decomposed into seven modules:

| Module | Single responsibility |
|---|---|
| `src/config.py` | Load and expose configuration |
| `src/data_loader.py` | Load raw CSV, fix data quality, derive target |
| `src/eda.py` | Profile missingness, compute prevalence, produce diagnostic plots |
| `src/preprocess.py` | Build sklearn preprocessing pipeline |
| `src/train.py` | Assemble model, cross-validate, fit |
| `src/evaluate.py` | Score on hold-out, produce performance plots |
| `main.py` | Orchestrate end-to-end run |

Each module imports only what it needs. The preprocessor can be lifted into a separate project; the data loader can be reused for a different modelling task; the evaluator is model-agnostic.

---

## 3. Automated and orchestrated

**Principle:** The full analysis runs end-to-end without manual intervention, with a single entry point.

**Evidence:**

- Single command to reproduce all results: `python main.py`.
- No notebook cells to execute in order.
- No interactive prompts.
- No manual file movement between stages.
- Expected runtime: approximately 5 seconds on a standard laptop.

The orchestrator (`main.py`) sequences the eight pipeline stages in order, with structured logging tracing each stage. A developer or reviewer can trace the full execution path by reading `main.py` top to bottom.

---

## 4. Documented

**Principle:** Every analytical choice is explained, at both code and project level, so a new team member can understand and extend the work.

**Evidence:**

- **Project-level:** `README.md` covers purpose, structure, quick start, configuration, and design decisions with rationale for each.
- **Module-level:** Every module opens with a docstring explaining its role in the pipeline.
- **Function-level:** Every function has a docstring explaining purpose, with type hints on arguments and return values.
- **Execution-level:** Structured logging at INFO level logs every pipeline stage, every transformation, and every metric computed.
- **Decision-level:** Key analytical choices (feature drops, missing data strategy, model selection, metric prioritisation) are explained in README.md Section "Key design decisions".

---

## 5. Tested

**Principle:** Critical transformations and the pipeline as a whole are covered by automated tests.

**Evidence:** `tests/test_pipeline.py` provides four tests:

| Test | Purpose |
|---|---|
| `test_fix_impossible_values_converts_zeros_to_nan` | Data quality transformation: impossible zeros become NaN, valid values untouched |
| `test_derive_target_is_binary` | Target derivation: num > 0 collapses to 0/1 correctly |
| `test_preprocessor_builds_without_error` | Preprocessor construction: both transformers registered |
| `test_pipeline_end_to_end_runs` | Smoke test: main.py runs to completion and produces AUC above chance (> 0.7) |

Tests run with `pytest tests/ -v`. All four pass. The smoke test in particular guards against silent regressions: any code change that breaks the pipeline or collapses model performance will fail this test.

---

## 6. Open source and reproducible

**Principle:** Anyone with access to the code and data can reproduce the results exactly, with no proprietary dependencies.

**Evidence:**

- All dependencies listed in `requirements.txt`, with minimum version bounds.
- Entirely open-source stack: Python, pandas, NumPy, scikit-learn, matplotlib, seaborn, joblib, PyYAML, pytest.
- No cloud services, no paid APIs, no licensed libraries.
- Deterministic random seed (`seed: 42` in `config.yaml`) applied consistently across train/test split, cross-validation fold assignment, and model initialisation.
- Verified: running `python main.py` twice, or in a clean environment, produces identical metrics (CV ROC-AUC = 0.890, Test ROC-AUC = 0.918, Test Recall = 0.902).

---

## Governance extensions required for production

The six RAP principles above are satisfied for this prototype. Production deployment of a clinical predictive model in the NHS requires additional controls that are out of scope for this technical test, but which would be the immediate next phase of work:

- **AQA sign-off.** Analytical Quality Assurance review against the standards in the Aqua Book.
- **DCB 0129 clinical safety case.** Required for any software that influences clinical decision-making in NHS care.
- **Data Protection Impact Assessment (DPIA).** Required before any real patient data is processed.
- **Model-governance review.** Sign-off from an NHS England model governance panel before deployment.
- **Information governance review.** Caldicott approval, s251 provisions if needed, and compliance with the Data Security and Protection Toolkit.
- **MLOps infrastructure.** Continuous monitoring for input drift, output drift, performance drift, and calibration drift. Automated retraining schedule.
- **Fairness audit.** Group-wise performance analysis by sex, age band, and any ethnicity fields that become available.
- **External validation.** Validation on contemporary NHS patient data before any clinical use. The training data here is from four research studies conducted in the late 1980s; it is not representative of present-day UK populations.
- **Clinician-facing explainability.** SHAP or equivalent local explanations, integrated into any clinician-facing interface.

---

## References

- [UK Government Analytical Community — Reproducible Analytical Pipelines](https://analysisfunction.civilservice.gov.uk/support/reproducible-analytical-pipelines/)
- [ONS — RAP guidance](https://dataingovernment.blog.gov.uk/2017/03/27/reproducible-analytical-pipeline/)
- [Aqua Book — Analytical Quality Assurance](https://www.gov.uk/government/publications/the-aqua-book-guidance-on-producing-quality-analysis-for-government)
- [NHS Digital — DCB 0129 Clinical Risk Management](https://digital.nhs.uk/services/clinical-safety)
