"""SHAP wrapper — genuine shap on trained pipeline; global + local artefacts."""
from __future__ import annotations
from pathlib import Path
import pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
def global_importance(model, X: pd.DataFrame, out_csv: str | Path) -> pd.DataFrame:
    import shap
    ex = shap.TreeExplainer(model) if hasattr(model, "estimators_") else shap.Explainer(model, X)
    sv = ex(X[:200])
    imp = pd.DataFrame({"feature": X.columns, "mean_abs_shap": abs(sv.values).mean(axis=0)}).sort_values("mean_abs_shap", ascending=False)
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True); imp.to_csv(out_csv, index=False)
    return imp
def waterfall(model, X: pd.DataFrame, idx: int, out_png: str | Path):
    import shap
    ex = shap.TreeExplainer(model) if hasattr(model, "estimators_") else shap.Explainer(model, X)
    sv = ex(X.iloc[[idx]])
    plt.figure(); import shap.plots as _p  # noqa
    shap.plots.waterfall(sv[0], show=False); plt.tight_layout(); plt.savefig(out_png, dpi=150); plt.close()
    return str(out_png)
