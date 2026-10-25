"""Generate fabricated rows for pipeline smoke-testing only; not real agricultural evidence."""
from pathlib import Path
import numpy as np
import pandas as pd
OUT = Path(__file__).parent / "data" / "crop_yield.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)
crops = ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane", "Pulses"]
bases = {"Wheat":2.7,"Rice":3.2,"Maize":4.1,"Cotton":1.6,"Sugarcane":65.0,"Pulses":0.9}
optima = {"Wheat":650,"Rice":1200,"Maize":800,"Cotton":750,"Sugarcane":1400,"Pulses":550}
rows=[]
for _ in range(1800):
 crop=str(rng.choice(crops)); rain=float(rng.uniform(200,2200)); temp=float(rng.uniform(12,38)); ph=float(rng.uniform(4.5,8.5)); irrigation=int(rng.integers(0,2))
 rain_factor=max(.25,1-abs(rain-optima[crop])/2200); temp_factor=max(.35,1-abs(temp-25)/45); ph_factor=max(.6,1-abs(ph-6.5)*.1)
 y=bases[crop]*rain_factor*temp_factor*ph_factor*(1.10 if irrigation else .85)+rng.normal(0,bases[crop]*.07)
 rows.append({"crop":crop,"rainfall_mm":round(rain,2),"temperature_c":round(temp,2),"soil_ph":round(ph,2),"irrigation":irrigation,"yield_tonnes_per_hectare":round(max(.01,y),3)})
pd.DataFrame(rows).to_csv(OUT,index=False)
print(f"Wrote {len(rows)} synthetic demo rows to {OUT}; not real agricultural evidence.")
