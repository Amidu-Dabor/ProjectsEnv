# services/training_service/app.py
from flask import Flask, request, jsonify, Response
from typing import List, Dict, Any
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global model and training configuration
TRAINED_MODEL = None
TRAINING_ARGS = None
MODEL_NAME: str = "distilbert-base-uncased"  # Use a lightweight model for demonstration

@app.route('/preprocess', methods=['POST'])
def preprocess() -> Response:
    """
    Preprocess raw text data by chunking into manageable documents.
    
    Expected JSON input:
        { "texts": ["text1", "text2", ...] }
    
    Returns a JSON list of preprocessed documents.
    """
    data: Dict[str, Any] = request.json
    texts: List[str] = data.get("texts", [])
    if not texts:
        return jsonify({"error": "No texts provided for preprocessing."}), 400

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(texts)
    processed_docs = [{"text": doc.page_content} for doc in docs]
    return jsonify({"processed_documents": processed_docs})

@app.route('/train', methods=['POST'])
def train() -> Response:
    """
    Train a classification model using provided training data.
    
    Expected JSON input:
        {
            "train_texts": ["text1", "text2", ...],
            "train_labels": [0, 1, ...],
            "num_epochs": 1  (optional)
        }
    
    Returns training status and parameters.
    """
    global TRAINED_MODEL, TRAINING_ARGS
    data: Dict[str, Any] = request.json
    train_texts: List[str] = data.get("train_texts", [])
    train_labels: List[int] = data.get("train_labels", [])
    num_epochs: int = data.get("num_epochs", 1)

    if not train_texts or not train_labels or len(train_texts) != len(train_labels):
        return jsonify({"error": "Training texts and labels must be provided and of equal length."}), 400

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    # Tokenize training data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True)

    class TrainDataset(torch.utils.data.Dataset):
        def __init__(self, encodings: Dict[str, List[int]], labels: List[int]) -> None:
            self.encodings = encodings
            self.labels = labels
        def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item
        def __len__(self) -> int:
            return len(self.labels)

    train_dataset = TrainDataset(train_encodings, train_labels)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=num_epochs,
        per_device_train_batch_size=8,
        logging_steps=10,
        logging_dir='./logs',
        no_cuda=not torch.cuda.is_available(),
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )
    trainer.train()
    TRAINED_MODEL = model
    TRAINING_ARGS = training_args

    return jsonify({"status": "Training complete", "num_epochs": num_epochs})

@app.route('/test', methods=['POST'])
def test() -> Response:
    """
    Test the trained model on provided test data.
    
    Expected JSON input:
        {
            "test_texts": ["text1", "text2", ...],
            "test_labels": [0, 1, ...]
        }
    
    Returns evaluation metrics (accuracy).
    """
    global TRAINED_MODEL
    if TRAINED_MODEL is None:
        return jsonify({"error": "No trained model available. Please train a model first."}), 400

    data: Dict[str, Any] = request.json
    test_texts: List[str] = data.get("test_texts", [])
    test_labels: List[int] = data.get("test_labels", [])
    if not test_texts or not test_labels or len(test_texts) != len(test_labels):
        return jsonify({"error": "Test texts and labels must be provided and of equal length."}), 400

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    test_encodings = tokenizer(test_texts, truncation=True, padding=True)

    class TestDataset(torch.utils.data.Dataset):
        def __init__(self, encodings: Dict[str, List[int]], labels: List[int]) -> None:
            self.encodings = encodings
            self.labels = labels
        def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item
        def __len__(self) -> int:
            return len(self.labels)

    test_dataset = TestDataset(test_encodings, test_labels)
    outputs = TRAINED_MODEL(**tokenizer(test_texts, return_tensors="pt", padding=True, truncation=True))
    predictions = torch.argmax(outputs.logits, dim=1).tolist()
    correct = sum([1 for pred, label in zip(predictions, test_labels) if pred == label])
    accuracy = correct / len(test_labels)
    return jsonify({"status": "Testing complete", "accuracy": accuracy})

if __name__ == '__main__':
    app.run(port=5007, debug=True)
