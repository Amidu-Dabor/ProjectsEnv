# Ad Click-Through-Rate Optimisation (Reinforcement Learning)

Finds the best of 10 ad versions while showing ads to 10,000 users, treating the choice as a **multi-armed bandit** problem: learn which ad gets the most clicks while wasting as few impressions as possible.

## What's inside

- **Upper Confidence Bound (UCB)**, in `Using Python/` and `Using R/`: picks the ad with the highest optimistic estimate of its click rate. Charts show the selections after 500, 1,000, 5,000 and 10,000 rounds.
- **Thompson Sampling** (`Using Python/`): samples each ad's click rate from a Beta distribution and shows the ad with the best draw. A chart shows the selections after 500 rounds.

Data: `Ads_CTR_Optimisation.csv`, a simulated table of which ads each user would click.

## Tech

Python (NumPy, pandas, Matplotlib, Seaborn) · R

## Run

Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
