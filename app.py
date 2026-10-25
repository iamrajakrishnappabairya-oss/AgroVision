from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
app = FastAPI(title="AgroVision Crop Yield API", version="1.0.0",
              description="Academic crop-yield prediction API. Validate all outputs against real agricultural data.")
# Public prototype: restrict allow_origins to your exact Netlify domain for production.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["GET","POST","OPTIONS"], allow_headers=["*"])

class PredictionInput(BaseModel):
    crop: str = Field(min_length=1, max_length=60)
    rainfall_mm: float = Field(ge=0, le=5000)
    temperature_c: float = Field(ge=-10, le=60)
    soil_ph: float = Field(ge=0, le=14)
    irrigation: int = Field(ge=0, le=1)

@app.get("/")
def root():
    return {"name":"AgroVision Crop Yield API","status":"online","note":"Academic prototype; confirm dataset provenance and model validity before practical use."}

@app.get("/health")
def health():
    return {"status":"ok","model_available":(ROOT/"model.joblib").exists()}

@app.get("/model-info")
def model_info():
    path = ROOT / "model.joblib"
    if not path.exists():
        return {"model_available": False, "message": "Train the model first."}
    bundle = joblib.load(path)
    return {"model_available": True, "model_source": bundle.get("model_source", "Trained regression model"), "dataset_source": bundle.get("dataset_source", "Unverified"), "warning": "Metrics and predictions are only as reliable as the dataset and validation design."}

@app.get("/metrics")
def metrics():
    path=ROOT/"metrics.json"
    if not path.exists():
        raise HTTPException(status_code=404,detail="No metrics file. Train the model first.")
    import json
    return json.loads(path.read_text())

@app.post("/predict")
def predict(payload: PredictionInput):
    path=ROOT/"model.joblib"
    if not path.exists():
        raise HTTPException(status_code=503,detail="Model not trained. Run train_model.py first.")
    bundle=joblib.load(path)
    frame=pd.DataFrame([payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()])
    value=float(bundle["pipeline"].predict(frame[bundle["features"]])[0])
    return {
        "predicted_yield_tonnes_per_hectare": round(max(0.0,value),3),
        "model_source": bundle.get("model_source","Trained regression model"),
        "validation_status": "demo_or_unverified_dataset",
        "warning": "Estimate only. Prediction quality depends on dataset quality, regional coverage and validation; do not treat as a guarantee of actual harvest."
    }
