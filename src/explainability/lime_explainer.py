"""LIME wrapper — complementary local explanations; compare with SHAP, neither proves causation."""
from __future__ import annotations
import pandas as pd
def explain_instance(pipeline, X_train: pd.DataFrame, instance: pd.Series, num_features=8) -> list[dict]:
    from lime.lime_tabular import LimeTabularExplainer
    num_cols = X_train.select_dtypes("number").columns.tolist()
    ex = LimeTabularExplainer(X_train[num_cols].values, feature_names=num_cols, mode="regression" if pipeline is not None else "regression", verbose=False, random_state=42)
    fn = (lambda a: pipeline.predict(pd.DataFrame(a, columns=num_cols)))
    exp = ex.explain_instance(instance[num_cols].values, fn, num_features=num_features)
    return [{"feature": f, "weight": float(w)} for f, w in exp.as_list()]
