# Sentence Similarity with BERT

Decides whether two sentences mean the same thing by comparing their **BERT embeddings**.

## How it works

A `BERTSimilarityEngine` class:
1. Encodes each sentence with a pre-trained BERT model (Hugging Face Transformers) and takes the `[CLS]` embedding.
2. Computes the cosine similarity between the two embeddings.
3. Labels the pair "similar" if the score is above a threshold (0.7).
4. Evaluates the predictions against labelled sentence pairs.

**Result: 73.3% accuracy** on the labelled pairs, using `bert-base-uncased`. The notebook ends with conceptual questions on how BERT embeddings capture meaning.

![Similarity scores](Sentence-pair%20similarity%20scores.png)

## Tech

Python · Hugging Face Transformers · TensorFlow · scikit-learn · Plotly

## Run

Open `nlp_with_transformers.ipynb` in Jupyter (`pip install transformers tensorflow scikit-learn plotly tabulate`).

A full write-up is in `NLP - Project Report.pdf`. *Built for the Data & AI programme at Cyber Shujaa, Kenya.*
