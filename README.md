# AgroVision — Complete Crop Yield Prediction Project

Attractive responsive dashboard + working FastAPI machine-learning API + training/evaluation pipeline + demo dataset + smoke test + deployment configuration.

## Read this first: accuracy honesty

This ZIP includes a **working Random Forest regression pipeline**, trained model artifact, and metrics so the software can be tested immediately. However, the bundled dataset is **synthetic/fabricated**. Any MAE/RMSE/R² shown from it measure only the demo pipeline; they are **not real-world agricultural accuracy** and must not be presented as proof that crop yields can be predicted accurately in real fields. No model can honestly promise 100% accuracy. To establish real performance, replace the dataset with trustworthy field/official data, document its source, and evaluate on appropriate unseen regions/seasons.

## What's included

- `frontend/` — responsive dashboard; overview, prediction form, methodology, error states, API connection and metrics display.
- `backend/app.py` — FastAPI endpoints: `/`, `/health`, `/model-info`, `/metrics`, `/predict`, and automatic `/docs`.
- `backend/train_model.py` — preprocessing pipeline, Random Forest regression, held-out test evaluation and metrics output.
- `backend/data/crop_yield.csv` — synthetic sample data for immediate smoke testing only.
- `backend/model.joblib` and `backend/metrics.json` — trained demo model and demo metrics.
- `backend/smoke_test.py` — verifies model artifact, prediction and metrics file.
- `render.yaml` — Render API deployment blueprint.
- `netlify.toml` — Netlify static frontend configuration.

## Easiest deployment (Netlify + Render)

### A. Deploy the website on Netlify

1. Extract this ZIP on your computer.
2. Open `https://app.netlify.com/drop`.
3. Drag **only the `frontend` folder** into Netlify Drop. The website UI will deploy.
4. This static website can show its clearly labelled demo estimate without an API. A real model prediction requires step B.

### B. Deploy the machine-learning API on Render

1. Upload the extracted project to a GitHub repository.
2. In Render, create a **Web Service** from that repository. Set Root Directory to `backend`.
3. Build command: `pip install -r requirements.txt && python generate_demo_data.py && python train_model.py`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Deploy and open `https://YOUR-API-URL/health`; expect JSON with `status: ok`. Check `/docs` for API docs.
6. Copy the base API URL (no `/predict` at the end). Open your Netlify site, go to **Yield prediction**, paste it in **API endpoint**, then run a prediction.
7. Free hosting may sleep when idle; the first request can be slow.

**Important:** Netlify Drop only hosts the static frontend; it does not start the Python API from this ZIP. For full-stack prediction, the API must be hosted separately or adapted to a serverless platform.

## Run locally on Windows

Install Python 3.10–3.12, then open Command Prompt in the extracted folder:

```bat
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_demo_data.py
python train_model.py
python smoke_test.py
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for API docs. In a second terminal, serve frontend:

```bat
cd frontend
py -m http.server 5173
```

Open `http://127.0.0.1:5173`, paste `http://127.0.0.1:8000` into API endpoint and run a prediction.

## Replace the sample with a real dataset

Expected CSV columns (exact names and units):

| Column | Meaning |
|---|---|
| `crop` | Crop category text |
| `rainfall_mm` | Rainfall in millimetres |
| `temperature_c` | Temperature in °C |
| `soil_ph` | Soil pH |
| `irrigation` | `0` = no, `1` = yes |
| `yield_tonnes_per_hectare` | Target yield in tonnes/hectare |

1. Back up the included synthetic CSV.
2. Put your real CSV at `backend/data/crop_yield.csv`. Ensure all values represent the same season/location granularity and yield unit.
3. Edit `backend/DATA_SOURCE.txt` to state the dataset's actual source, license, geography and years. Do not label data as real unless it is.
4. Train again with `python train_model.py`, run `python smoke_test.py`, and review `backend/metrics.json`.
5. For credible evaluation, consider a time-based or region-held-out test rather than only a random split; check data leakage, target consistency and baseline performance.

The current model uses crop, rainfall, temperature, pH and irrigation only. It does not account for every factor (seed variety, fertilizer, pests, soil type, growing degree days, location, etc.), so real predictions may be unreliable outside the training data.

## Folder layout

```text
AgroVision_Complete/
├── frontend/                 # Deploy this folder to Netlify Drop
├── backend/                  # Deploy this folder as Python API
│   ├── app.py
│   ├── train_model.py
│   ├── generate_demo_data.py
│   ├── smoke_test.py
│   ├── model.joblib
│   ├── metrics.json
│   ├── DATA_SOURCE.txt
│   └── data/crop_yield.csv
├── netlify.toml
├── render.yaml
└── README.md
```
