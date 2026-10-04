"""EDA — correlation is not causation. Saves plots + tables to reports/eda/."""
from __future__ import annotations
from pathlib import Path
import pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
def run(inp="data/processed/clean_master_dataset.csv", out="reports/eda"):
    o = Path(out); o.mkdir(parents=True, exist_ok=True)
    try: df = pd.read_csv(inp)
    except FileNotFoundError: df = pd.read_csv("data/raw/mango_microbiome_dataset.csv")
    desc = df.describe(include="number").T; desc.to_csv(o/"numeric_summary.csv")
    for c in ["Village","Mango_Variety","Disease_Risk","Nutrient_Availability"]:
        if c in df.columns: df[c].value_counts().to_csv(o/f"dist_{c}.csv")
    num = df.select_dtypes("number")
    corr = num.corr(numeric_only=True)
    if "Mango_Yield" in corr.columns:
        corr["Mango_Yield"].sort_values(ascending=False).to_csv(o/"corr_with_yield.csv")
    plt.figure(figsize=(8,5)); df["Mango_Yield"].hist(bins=40); plt.title("Mango_Yield (kg/tree)"); plt.xlabel("kg/tree"); plt.tight_layout(); plt.savefig(o/"yield_hist.png"); plt.close()
    if "Village" in df.columns:
        plt.figure(figsize=(8,5)); df.boxplot(column="Mango_Yield", by="Village"); plt.title("Yield by village"); plt.suptitle(""); plt.tight_layout(); plt.savefig(o/"yield_by_village.png"); plt.close()
    (o/"README.md").write_text("# EDA\nCorrelation ≠ causation. See corr_with_yield.csv.\n")
    print(f"EDA → {o}, shape {df.shape}")
if __name__ == "__main__": run()
