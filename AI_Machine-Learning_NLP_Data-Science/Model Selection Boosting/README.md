# Model Selection and XGBoost

Techniques for choosing and tuning a model reliably rather than trusting a single train/test split.

## What's inside

| Notebook | Technique | Result (saved run) |
|---|---|---|
| `Model Selection/k_fold_cross_validation.ipynb` | 40-fold cross-validation of a kernel SVM on social-network ad data | 90.8% mean accuracy |
| `Model Selection/grid_search.ipynb` | Grid search over SVM kernels and `C`/`gamma` values | 91.2% best accuracy |
| `XGBoost/xg_boost.ipynb` | XGBoost classifier on breast-cancer cell data, with k-fold validation | not yet run (no saved output) |

## Tech

Python · scikit-learn · XGBoost · pandas

## Run

`pip install xgboost`, then: Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
