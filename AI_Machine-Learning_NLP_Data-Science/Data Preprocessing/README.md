# Data Preprocessing

Reusable steps for preparing raw data before training a model, in Python and R.

## What's inside

- `Using Python/Data Preprocessing.ipynb`: fills missing values with the mean (`SimpleImputer`), one-hot encodes categorical columns (`ColumnTransformer`), label-encodes the target, splits into training and test sets, and scales features.
- `Using Python/Building a Logistic Regression.ipynb`: a statsmodels logistic regression on bank marketing data, checking whether a campaign led customers to subscribe.
- `Using R/Data Preprocessing.R`: the same preprocessing steps in R.
- `Dummy_Variables_Intuition.png`: a diagram explaining dummy variables.

## Tech

Python (pandas, scikit-learn, statsmodels) · R

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
