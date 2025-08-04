from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pickle

# Load the trained model
with open("california_knn_pipeline.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI(title="California Housing Price Predictor", version="1.0")

# Define expected input format
class InputData(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the California Housing Price Predictor API 🚀"}

@app.post("/predict")
def predict(data: InputData):
    # Convert input data to DataFrame with column names
    input_df = pd.DataFrame([data.model_dump()])
    
    # Predict
    prediction = model.predict(input_df)
    
    return {"predicted_house_value": round(float(prediction[0]), 3)}
