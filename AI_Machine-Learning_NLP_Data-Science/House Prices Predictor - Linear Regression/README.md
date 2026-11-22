# House Price Predictor (Linear Regression)

Predicts house prices with **simple** (one feature) and **multiple** (several features) linear regression, using a reusable `LinearRegressionModel` class.

## Results (test set, from the saved runs)

| Model | R² | RMSE |
|---|---|---|
| Simple linear regression | 0.99 | 19,513 |
| Multiple linear regression | 0.96 | 31,588 |

The notebook also includes the scripts that generated the larger synthetic datasets (`homeprices.csv`, `homeprices-m.csv`), including a version with deliberately missing values, so the cleaning steps can be tested.

## Tech

Python · scikit-learn · pandas · NumPy · Matplotlib

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
