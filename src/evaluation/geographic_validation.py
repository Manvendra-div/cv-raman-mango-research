"""Geographic hold-out: train Malihabad/Kakori/Mall → test Rahimabad. No leakage: fit preprocessors on train only."""
from __future__ import annotations
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score
HOLDOUT = "Rahimabad"
def split(df: pd.DataFrame):
    tr = df[df.Village != HOLDOUT]; te = df[df.Village == HOLDOUT]
    return tr, te
def evaluate(df: pd.DataFrame, target: str, estimator) -> dict:
    tr, te = split(df)
    num = tr.select_dtypes("number").columns.drop([target], errors="ignore").tolist()
    cat = [c for c in ["Village","Mango_Variety","Soil_Depth","Sampling_Season","Management"] if c in tr.columns]
    pre = ColumnTransformer([("n", StandardScaler(), num), ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
    pipe = Pipeline([("pre", pre), ("m", estimator)])
    pipe.fit(tr[num+cat], tr[target])
    pred = pipe.predict(te[num+cat])
    out = {"train_n": len(tr), "holdout_n": len(te), "holdout": HOLDOUT}
    if "Yield" in target: out.update({"rmse": float(mean_squared_error(te[target], pred) ** 0.5)})
    else: out.update({"accuracy": float(accuracy_score(te[target], pred)), "macro_f1": float(f1_score(te[target], pred, average="macro"))})
    return out
