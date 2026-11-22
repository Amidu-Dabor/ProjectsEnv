# French Flash Cards (Tkinter)

A flash-card app for learning French vocabulary. Each card shows a French word, then flips to the English meaning after 4 seconds.

## How it works

- Loads words from `data/french_words.csv`.
- Click ✔ when you know a word: it is removed and your progress is saved to `data/words_to_learn.csv`, so it isn't shown again.
- Click ✘ to keep the word in the deck.

## Tech

Python · Tkinter · pandas

## Run

```bash
pip install pandas
cd "Flash Card Project"
python main.py
```
