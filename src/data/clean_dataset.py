"""Cleaning: raw → data/processed/clean_master_dataset.csv (raw immutable)."""
from __future__ import annotations
import argparse
import pandas as pd, numpy as np
from pathlib import Path
from src.data.data_schema import TAXA_COLS, NUMERIC_RANGES

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    # normalise dash variants in Soil_Depth
    if "Soil_Depth" in df.columns:
        df["Soil_Depth"] = df["Soil_Depth"].astype(str).str.replace("–", "-", regex=False)
    # biologically justified: relative abundance cannot be negative → clip + renormalise
    # rationale documented in DATA_QUALITY_REPORT: negatives are synthetic artefact, not log-transform
    present = [c for c in TAXA_COLS if c in df.columns]
    if present:
        df[present] = df[present].clip(lower=0)
        row_sum = df[present].sum(axis=1).replace(0, np.nan)
        # only renormalise rows that originally summed ~100 (compositional); else keep clipped
        mask = row_sum.between(90, 110)
        df.loc[mask, present] = df.loc[mask, present].div(row_sum[mask], axis=0) * 100
    # texture closure Sand+Silt+Clay=100 where present
    if {"Sand","Silt","Clay"} <= set(df.columns):
        t = df[["Sand","Silt","Clay"]].sum(axis=1)
        m = t.between(95, 105) & (t != 0)
        df.loc[m, ["Sand","Silt","Clay"]] = df.loc[m, ["Sand","Silt","Clay"]].div(t[m], axis=0) * 100
    return df

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--input", default="data/raw/mango_microbiome_dataset.csv")
    ap.add_argument("--out", default="data/processed/clean_master_dataset.csv")
    a = ap.parse_args()
    df = pd.read_csv(a.input)
    out = clean(df)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.out, index=False)
    print(f"rows {len(df)} → {len(out)}, saved {a.out}")
