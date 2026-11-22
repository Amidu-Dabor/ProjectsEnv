# Restaurant Review Sentiment (NLP)

Classifies 1,000 restaurant reviews as positive or negative.

## How it works

1. **Clean the text:** lowercase it, remove punctuation and stop words (keeping "not", which flips meaning), and stem each word with NLTK's Porter stemmer.
2. **Bag of words:** turn each review into word counts with `CountVectorizer`.
3. **Classify:** train a Naive Bayes model and evaluate it with a confusion matrix.

**Result: 79% test accuracy.**

## Tech

Python · NLTK · scikit-learn · pandas

## Run

`pip install nltk`, then: Run the notebooks with Jupyter (`pip install jupyter pandas numpy matplotlib seaborn scikit-learn`), from inside their own folder so the CSV paths resolve.
