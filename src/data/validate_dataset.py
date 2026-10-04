"""Dataset validation — biological + statistical checks. Raw is never modified."""
from __future__ import annotations
import argparse, json
import pandas as pd
from pathlib import Path
from src.data.data_schema import NUMERIC_RANGES, TAXA_COLS, CATEGORICAL

def validate(df: pd.DataFrame) -> dict:
    issues = {"missing": {}, "duplicates": {}, "range_violations": {}, "taxa": {}, "targets": {}}
    issues["missing"] = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}
    issues["duplicates"] = {"full_rows": int(df.duplicated().sum()),
        "sample_id": int(df.duplicated("Sample_ID").sum()) if "Sample_ID" in df.columns else 0}
    rv = {}
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col in df.columns:
            n = int(((df[col] < lo) | (df[col] > hi)).sum())
            if n: rv[col] = {"count": n, "min": float(df[col].min()), "max": float(df[col].max()), "allowed": [lo, hi]}
    issues["range_violations"] = rv
    neg = {c: int((df[c] < 0).sum()) for c in TAXA_COLS if c in df.columns and (df[c] < 0).any()}
    issues["taxa"]["negative_counts"] = neg
    if set(TAXA_COLS) <= set(df.columns):
        s = df[TAXA_COLS].sum(axis=1)
        issues["taxa"]["composition_sum_mean"] = float(s.mean())
        issues["taxa"]["composition_sum_minmax"] = [float(s.min()), float(s.max())]
    for t in ["Disease_Risk","Nutrient_Availability","Village","Orchard_ID"]:
        if t in df.columns: issues["targets"][t] = df[t].value_counts().to_dict()
    return issues

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--input", default="data/raw/mango_microbiome_dataset.csv")
    ap.add_argument("--out", default="outputs/data_quality_audit_results.json")
    a = ap.parse_args()
    df = pd.read_csv(a.input)
    res = {"shape": list(df.shape), **validate(df)}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({"shape": res["shape"], "neg_taxa": res["taxa"].get("negative_counts", {}),
        "targets": res["targets"]}, indent=2))
