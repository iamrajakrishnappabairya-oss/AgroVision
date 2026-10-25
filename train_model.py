"""Train a Random Forest regression model and evaluate on a held-out split. Demo data is synthetic."""
from pathlib import Path
import json, joblib, numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
ROOT=Path(__file__).parent; DATA=ROOT/"data"/"crop_yield.csv"; MODEL_PATH=ROOT/"model.joblib"; METRICS_PATH=ROOT/"metrics.json"; SOURCE_PATH=ROOT/"DATA_SOURCE.txt"
FEATURES=["crop","rainfall_mm","temperature_c","soil_ph","irrigation"]; TARGET="yield_tonnes_per_hectare"
def main():
 if not DATA.exists(): raise FileNotFoundError(f"{DATA} not found. Put a CSV there or run generate_demo_data.py.")
 df=pd.read_csv(DATA); missing=[c for c in FEATURES+[TARGET] if c not in df.columns]
 if missing: raise ValueError(f"Dataset missing required columns: {missing}")
 df=df[FEATURES+[TARGET]].replace([np.inf,-np.inf],np.nan).dropna(subset=[TARGET])
 if len(df)<30: raise ValueError("Need at least 30 labelled rows for a basic train/test experiment.")
 X=df[FEATURES]; y=pd.to_numeric(df[TARGET],errors="coerce"); valid=y.notna(); X=X.loc[valid]; y=y.loc[valid].astype(float)
 X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=42)
 numeric=["rainfall_mm","temperature_c","soil_ph","irrigation"]; categorical=["crop"]
 prep=ColumnTransformer([("numeric",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("categorical",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),categorical)])
 model=Pipeline([("prep",prep),("regressor",RandomForestRegressor(n_estimators=250,min_samples_leaf=2,random_state=42,n_jobs=-1))])
 baseline=Pipeline([("prep",prep),("regressor",DummyRegressor(strategy="mean"))]); model.fit(X_train,y_train); baseline.fit(X_train,y_train); pred=model.predict(X_test)
 source=SOURCE_PATH.read_text().strip() if SOURCE_PATH.exists() else "UNVERIFIED DATASET — document source and validation"; synthetic=source.lower().startswith("synthetic")
 metrics={"rows_total":int(len(df)),"train_rows":int(len(X_train)),"test_rows":int(len(X_test)),"mae":round(float(mean_absolute_error(y_test,pred)),4),"rmse":round(float(np.sqrt(mean_squared_error(y_test,pred))),4),"r2":round(float(r2_score(y_test,pred)),4),"baseline_mae":round(float(mean_absolute_error(y_test,baseline.predict(X_test))),4),"dataset_source":source,"validation_status":"DEMO_ONLY_NOT_REAL_WORLD_VALIDATION" if synthetic else "OWNER_MUST_VERIFY_DATASET_AND_VALIDATION","dataset_note":"SYNTHETIC DEMO DATA — scores only test the software pipeline; they are not evidence of real-world crop-yield accuracy." if synthetic else "Verify provenance, units, leakage controls, and regional/time-based validation before reporting these scores.","features":FEATURES,"target":TARGET}
 joblib.dump({"pipeline":model,"features":FEATURES,"model_source":"Random Forest Regressor (synthetic demo data)" if synthetic else "Random Forest Regressor (dataset source requires owner verification)","dataset_source":source},MODEL_PATH); METRICS_PATH.write_text(json.dumps(metrics,indent=2)); print(json.dumps(metrics,indent=2)); print("Saved model:",MODEL_PATH)
if __name__=="__main__": main()
