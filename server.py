from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import joblib
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import TrafficDatabase
import pandas as pd

app = FastAPI(title="Traffic Prediction API")

# Ajout du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou spécifiez ["http://localhost:5173"] pour plus de sécurité
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the saved model and scaler
try:
    model = joblib.load('models/traffic_model.joblib')
    scaler = joblib.load('models/traffic_scaler.joblib')
except Exception as e:
    raise Exception("Failed to load model and scaler. Make sure to run save_model.py first.")

# Initialize database connection
db = TrafficDatabase()

class PredictionRequest(BaseModel):
    date: str  # Format: "DD/MM/YYYY HH:MM"

@app.get("/")
async def root():
    return {"message": "Traffic Prediction API is running"}

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # Parse the date
        date = datetime.strptime(request.date, "%d/%m/%Y %H:%M")
        
        # Create features
        features = [[
            date.hour,
            date.weekday(),
            date.day,
            date.month
        ]]
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        return {
            "date": request.date,
            "predicted_traffic": float(prediction),
            "unit": "bits/s"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use DD/MM/YYYY HH:MM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_day")
async def predict_day(request: PredictionRequest):
    try:
        # Parse the date
        base_date = datetime.strptime(request.date, "%d/%m/%Y %H:%M")
        
        # Generate predictions for each hour of the day
        predictions = []
        for hour in range(24):
            current_date = base_date.replace(hour=hour, minute=0)
            features = [[
                current_date.hour,
                current_date.weekday(),
                current_date.day,
                current_date.month
            ]]
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            predictions.append({
                "date": current_date.strftime("%d/%m/%Y %H:%M"),
                "predicted_traffic": float(prediction),
                "unit": "bits/s"
            })
        
        return predictions
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use DD/MM/YYYY HH:MM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/traffic_data")
async def get_traffic_data():
    try:
        # Récupérer toutes les données de trafic depuis la base de données
        df = db.get_all_traffic_data()
        if df.empty:
            return {"message": "Aucune donnée trouvée dans la base de données."}
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True) 