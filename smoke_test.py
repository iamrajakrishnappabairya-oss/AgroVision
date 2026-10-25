"""Quick offline test of the saved model and required files."""
from pathlib import Path
import json, joblib, pandas as pd
ROOT=Path(__file__).parent
required=[ROOT/"model.joblib", ROOT/"metrics.json", ROOT/"data"/"crop_yield.csv"]
missing=[str(p) for p in required if not p.exists()]
if missing: raise SystemExit(f"Missing required files: {missing}")
bundle=joblib.load(ROOT/"model.joblib")
row=pd.DataFrame([{"crop":"Wheat","rainfall_mm":650,"temperature_c":22,"soil_ph":6.5,"irrigation":1}])
y=float(bundle["pipeline"].predict(row[bundle["features"]])[0])
m=json.loads((ROOT/"metrics.json").read_text())
assert y >= 0 and all(k in m for k in ["mae","rmse","r2","dataset_note"])
print("PASS: model artifact loads; prediction=%.3f t/ha; metrics file exists." % y)
print("DATA NOTE:",m["dataset_note"])
