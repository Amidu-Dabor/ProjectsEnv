# Market Basket Analysis (Association Rule Learning)

Finds which products are often bought together in 7,500 shopping-basket transactions, to support decisions like product placement and bundle offers.

## What's inside

- **Apriori** (`Using Python/Apriori/`): finds rules such as "customers who buy X also buy Y", ranked by lift, confidence and support.
- **Eclat** (`Using Python/Eclat/`): finds frequent product pairs ranked by support. For example, mushroom cream sauce and escalope appear together in about 0.57% of baskets.

## Tech

Python · apyori · pandas · Matplotlib · Seaborn

## Run

`pip install apyori`, then: Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
