
from pathlib import Path
import json
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "model.joblib"

app = FastAPI(
    title="AgroVision Crop Yield API",
    version="1.1.0",
    description="Academic crop-yield prediction API."
)

# Allow frontend requests from Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


class PredictionInput(BaseModel):
    crop: str = Field(min_length=1, max_length=60)
    rainfall_mm: float = Field(ge=0, le=5000)
    temperature_c: float = Field(ge=-10, le=60)
    soil_ph: float = Field(ge=0, le=14)
    irrigation: int = Field(ge=0, le=1)


@app.get("/")
def root():
    return {
        "name": "AgroVision Crop Yield API",
        "status": "online",
        "health": "/api/health",
        "prediction": "/api/predict",
        "docs": "/docs"
    }


# Support both health-check URLs
@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_available": MODEL_PATH.exists()
    }


@app.get("/model-info")
@app.get("/api/model-info")
def model_info():
    if not MODEL_PATH.exists():
        return {
            "model_available": False,
            "message": "Model file is missing."
        }

    try:
        bundle = joblib.load(MODEL_PATH)
        return {
            "model_available": True,
            "model_source": bundle.get(
                "model_source", "Trained regression model"
            ),
            "dataset_source": bundle.get(
                "dataset_source", "Unverified"
            ),
            "warning": (
                "Predictions depend on the training data "
                "and have not been validated for real-world accuracy."
            )
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load model: {str(exc)}"
        )


@app.get("/metrics")
@app.get("/api/metrics")
def metrics():
    metrics_path = ROOT / "metrics.json"

    if not metrics_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Metrics file not found."
        )

    return json.loads(metrics_path.read_text())


# Support both prediction endpoint URLs
@app.post("/predict")
@app.post("/api/predict")
def predict(payload: PredictionInput):
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Model file is missing. Train the model first."
        )

    try:
        bundle = joblib.load(MODEL_PATH)

        data = (
            payload.model_dump()
            if hasattr(payload, "model_dump")
            else payload.dict()
        )

        features = bundle["features"]
        frame = pd.DataFrame([data])

        missing = [f for f in features if f not in frame.columns]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Model features missing: {missing}"
            )

        value = float(
            bundle["pipeline"].predict(frame[features])[0]
        )

        return {
            "predicted_yield_tonnes_per_hectare": round(
                max(0.0, value), 3
            ),
            "model_source": bundle.get(
                "model_source", "Trained regression model"
            ),
            "validation_status": "demo_or_unverified_dataset",
            "warning": (
                "Estimate only. The model was tested using synthetic "
                "demo data and is not validated for real-world "
                "agricultural accuracy."
            )
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}"
        )
