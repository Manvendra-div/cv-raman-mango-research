from src.recommendations.rule_engine import evaluate
from src.evaluation.geographic_validation import split
from src.zone_intelligence.yield_gap import YieldGapAnalyzer
from src.zone_intelligence.reference_yield import ReferenceYield
import pandas as pd
def test_rule_fires_on_measured_zn():
    r = evaluate({"Zn": 0.2, "Organic_Carbon": 0.6, "pH": 7.0, "Pathogen_Load_Index": 0.2, "Available_K": 200})
    assert any(x["rule_id"] == "ZN_LOW" for x in r)
def test_no_fake_dose():
    r = evaluate({"Zn": 0.2, "Organic_Carbon": 0.6, "pH": 7.0, "Pathogen_Load_Index": 0.2, "Available_K": 200})
    assert "kg/ha prescribe" not in str(r).lower() or "do not" in str(r).lower()
def test_geo_split_no_leak():
    df = pd.DataFrame({"Village": ["Malihabad", "Rahimabad"], "Mango_Yield": [20, 21]})
    tr, te = split(df)
    assert set(te.Village) == {"Rahimabad"} and set(tr.Village) == {"Malihabad"}
def test_gap_math():
    ref = ReferenceYield(mean=51, median=50, q75=60, q90=63, top10_mean=65, std=2, min=40, max=70, sample_count=100, orchard_count=10, source_description="t", warnings=[])
    g = YieldGapAnalyzer().primary_gap(47, ref)
    assert g.gap_absolute == round(60 - 47, 2) and g.reference_type == "q75"
