# California House Prices: Real-time Inference API (MLOps)

Trains a K-Nearest-Neighbours model on the California Housing dataset and serves it as a **REST API with FastAPI**, so other apps can get price predictions in real time.

## How it works

1. **Train** (`mlops_house_prices.ipynb`): a `HousingModel` class explores the data, builds a scikit-learn pipeline (scaling + KNN), tunes it with grid search, evaluates it (test RMSE 0.60, in units of $100,000) and saves it to `california_knn_pipeline.pkl`.
2. **Serve** (`mlops_fastapi/main.py`): loads the pipeline at start-up and exposes:
   - `GET /`: a health message
   - `POST /predict`: takes the 8 housing features and returns a predicted price. Input is validated with a Pydantic model.

## Run the API

```bash
cd mlops_fastapi
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs to try it. Example request:

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" \
  -d '{"MedInc": 8.3, "HouseAge": 41, "AveRooms": 6.9, "AveBedrms": 1.0, "Population": 322, "AveOccup": 2.5, "Latitude": 37.88, "Longitude": -122.23}'
```

## Tech

Python · scikit-learn · FastAPI · Pydantic · Uvicorn · pandas

A full write-up is in `MLOPS - Project Report.pdf`. *Built for the Data & AI programme at Cyber Shujaa, Kenya.*
