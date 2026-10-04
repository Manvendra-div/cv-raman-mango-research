"""Orchard-level validation: GroupKFold by Orchard_ID. Correlated rows from same orchard never split across folds."""
from __future__ import annotations
import pandas as pd, numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, accuracy_score
def group_cv(df: pd.DataFrame, target: str, estimator, n_splits=5) -> dict:
    groups = df["Orchard_ID"]; X = df.drop(columns=[target])
    num = X.select_dtypes("number").columns.tolist(); cat = [c for c in ["Village","Mango_Variety","Soil_Depth","Sampling_Season","Management"] if c in X.columns]
    scores = []
    for tri, tei in GroupKFold(n_splits=n_splits).split(X, df[target], groups):
        pre = ColumnTransformer([("n", StandardScaler(), num), ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
        pipe = Pipeline([("pre", pre), ("m", estimator)]); pipe.fit(X.iloc[tri][num+cat], df[target].iloc[tri])
        p = pipe.predict(X.iloc[tei][num+cat]); y = df[target].iloc[tei]
        scores.append(float(mean_squared_error(y, p) ** 0.5) if "Yield" in target else float(accuracy_score(y, p)))
    return {"metric": "rmse" if "Yield" in target else "accuracy", "fold_scores": scores, "mean": float(np.mean(scores)), "n_orchards": int(df.Orchard_ID.nunique())}
