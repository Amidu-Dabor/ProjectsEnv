# E-commerce User Action Classifier (NumPy from scratch)

Predicts which of four actions a visitor takes on an e-commerce site from their session data (device, products viewed, visit duration, returning visitor, time of day), using models written **from scratch in NumPy**, without an ML library.

## What's inside

| Notebook | What it does |
|---|---|
| `process.ipynb` | Loads `ecommerce_data.csv`, one-hot encodes the time-of-day feature, normalises numeric columns and builds a binary subset |
| `logistic_softmax_train.ipynb` | Multi-class logistic (softmax) regression trained with gradient descent and cross-entropy loss |
| `ann_train.ipynb` | A one-hidden-layer neural network with a softmax output, forward pass and backpropagation by hand |

## Results (from the saved runs)

| Model | Train accuracy | Test accuracy |
|---|---|---|
| Softmax regression | 90.3% | 95.0% |
| Neural network (1 hidden layer) | 97.8% | 92.0% |

## Tech

Python · NumPy · pandas · Matplotlib

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
