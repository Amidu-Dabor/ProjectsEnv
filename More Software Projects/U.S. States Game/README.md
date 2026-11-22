# U.S. States Quiz Game

A map quiz: type the names of the 50 U.S. states, and each correct answer is written onto a blank map in the right place.

## How it works

- Loads state names and map coordinates from `50_states.csv` with pandas.
- Shows a blank U.S. map (`blank_states_img.gif`) in a turtle window and asks for state names.
- Type `Exit` to stop: the states you missed are saved to `missing-states-to-learn.csv`.

## Tech

Python · turtle · pandas

## Run

```bash
pip install pandas
python main.py
```
