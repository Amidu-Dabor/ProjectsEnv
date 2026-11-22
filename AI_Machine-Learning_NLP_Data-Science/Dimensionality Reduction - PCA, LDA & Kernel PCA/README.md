# Dimensionality Reduction: PCA, LDA and Kernel PCA

Compares three ways of compressing the 13 chemical features of the **Wine** dataset into 2 dimensions, then classifies the wine's customer segment with logistic regression on the reduced data.

## Results (test set, from the saved runs)

| Method | Type | Accuracy |
|---|---|---|
| PCA (Principal Component Analysis) | unsupervised | 97.2% |
| LDA (Linear Discriminant Analysis) | supervised | 100% |
| Kernel PCA (RBF kernel) | unsupervised, non-linear | 100% |

Each folder also has decision-region plots for the training and test sets.

## Tech

Python · scikit-learn · pandas · Matplotlib · Seaborn

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
