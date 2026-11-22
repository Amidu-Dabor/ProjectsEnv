# Classification Models: Comparison

The same problems solved with seven classic classification algorithms, to compare how each performs.

## 1. Breast cancer detection: `Best Classification Model Selection/`

Classifies tumour cells as benign or malignant (Wisconsin breast cancer data, `Data.csv`).

| Model | Test accuracy |
|---|---|
| Decision tree | 95.9% |
| Kernel SVM | 95.3% |
| Logistic regression | 94.7% |
| K-nearest neighbours | 94.2% |
| Naive Bayes | 94.2% |
| Linear SVM | 94.2% |
| Random forest | 93.6% |

## 2. Customer conversion prediction: `Customer conversion and CTR …/` folders

Predicts whether a social-network user buys a product after seeing an ad, from their age and estimated salary (`Social_Network_Ads.csv`).

| Model | Test accuracy |
|---|---|
| K-nearest neighbours | 95.0% |
| Kernel SVM | 95.0% |
| Logistic regression | 92.5% |
| Naive Bayes | 91.25% |
| Random forest | 91.25% |
| Linear SVM | 91.25% |
| Decision tree | 90.0% |

Each folder includes decision-boundary plots for the training and test sets. `Best Classification Model Selection/Regression/` contains reusable regression templates.

## Tech

Python · scikit-learn · pandas · Matplotlib

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
