"""Personalized farmer explainer — easy words (EN + HI) + what-if growth visuals.

Integrity: growth bars are MODEL estimates from counterfactual inputs, not
proven field gains. Every output carries a disclaimer. Never prescribes doses.
Picks the most critical limiting factors per orchard (severity-ranked).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

DISCLAIMER_EN = (
    "Model estimate only (synthetic-data prototype). Actual field results vary. "
    "Confirm with soil test + local agronomist before action."
)
DISCLAIMER_HI = (
    "Yah keval model ka anumaan hai (practice data par bana). Khet ka asli parinaam alag ho sakta hai. "
    "Mitti jaanch + sthaniya krishi vigyani se pushti karke hi kadam uthayein."
)

# Easy-words per feature: (do_en, do_hi, dont_en, dont_hi)
EASY_WORDS: Dict[str, Dict[str, str]] = {
    "Zn": {"do_en": "Get soil zinc checked; discuss zinc care with agronomist",
           "do_hi": "Mitti me jasta (zinc) ki jaanch karayein; krishi vigyani se salah lein",
           "dont_en": "Do not add zinc chemical on your own",
           "dont_hi": "Apne aap zinc dawai na daalein",
           "why_en": "Low zinc can slow leaf and fruit growth",
           "why_hi": "Kam jasta se patti-fal ki badhwar dheemi ho sakti hai"},
    "Organic_Carbon": {"do_en": "Add compost / well-rotted farmyard manure as advised locally",
           "do_hi": "Sthaniya salah se compost / sadi gobar khaad daalein",
           "dont_en": "Do not burn crop residue; do not dump raw waste",
           "dont_hi": "Fasal avashesh na jalayein; kachcha kachra na daalein",
           "why_en": "Organic matter feeds soil life and holds nutrients",
           "why_hi": "Jeevansh mitti ke jeevon ko khaad deta hai aur poshak rokta hai"},
    "pH": {"do_en": "Get pH retested; discuss gypsum / organic options with expert",
           "do_hi": "pH dobara jaanch karayein; vigyani se sudhaar upay poochein",
           "dont_en": "Do not pour chemicals to change pH quickly",
           "dont_hi": "pH turant badalne ke liye tez chemical na daalein",
           "why_en": "Very high/low pH locks nutrients away from roots",
           "why_hi": "Bahut uncha-neecha pH jadon tak poshak nahi pahunchne deta"},
    "Pathogen_Load_Index": {"do_en": "Walk the orchard; check drainage, fallen fruit, pruning hygiene",
           "do_hi": "Bagiche ka nirikshan karein; jal-nikasi, gire fal, katai-chhatai safai dekhein",
           "dont_en": "Do not spray fungicide without diagnosis",
           "dont_hi": "Bina jaanch ke phaphundi-naashak na chhidkein",
           "why_en": "High pathogen signal means higher disease risk",
           "why_hi": "Uncha rog-sanket ka arth hai bimari ka adhik khatra"},
    "Available_K": {"do_en": "Confirm potassium test; follow local K schedule",
           "do_hi": "Potash jaanch ki pushti karein; sthaniya karyakram apnayein",
           "dont_en": "Do not overdose potash",
           "dont_hi": "Potash adhik matra me na daalein",
           "why_en": "Potassium supports fruit size and quality",
           "why_hi": "Potash fal ke aakaar aur gunvatta me madad karta hai"},
    "Available_P": {"do_en": "Confirm phosphorus test; follow local P schedule",
           "do_hi": "Phosphorus jaanch karayein; sthaniya matra apnayein",
           "dont_en": "Do not add extra DAP/SSP without advice",
           "dont_hi": "Bina salah ke atirikt khaad na daalein",
           "why_en": "Phosphorus supports roots and flowering",
           "why_hi": "Phosphorus jadon aur phool me madad karta hai"},
    "Total_Nitrogen": {"do_en": "Check nitrogen with soil test; split doses as advised",
           "do_hi": "Mitti jaanch se nitrogen dekhein; salah se kishton me dein",
           "dont_en": "Do not give heavy urea at once",
           "dont_hi": "Ek saath bhari urea na dein",
           "why_en": "Too little or too much nitrogen both harm yield",
           "why_hi": "Kam ya adhik dono nitrogen nuksaan karte hain"},
    "EC": {"do_en": "Improve drainage; use good-quality irrigation water",
           "do_hi": "Jal-nikasi sudharein; achche paani se sinchai karein",
           "dont_en": "Do not keep flooding with salty water",
           "dont_hi": "Khare paani se baar-baar na bharein",
           "why_en": "Salty soil stresses roots",
           "why_hi": "Namkeen mitti jadon ko nuksaan pahunchati hai"},
    "Soil_Moisture": {"do_en": "Mulch basins; irrigate evenly in dry spells",
           "do_hi": "Thaalon me mulching karein; sukhe me saman sinchai dein",
           "dont_en": "Do not waterlog the basin",
           "dont_hi": "Thaalon me paani na bhare rehne dein",
           "why_en": "Even moisture protects feeder roots",
           "why_hi": "Saman nami poshak jadon ki raksha karti hai"},
    "Fe": {"do_en": "Get iron checked especially if leaves yellow with green veins",
           "do_hi": "Patti peeli-nas hari dikhe to loha (iron) jaanch karayein",
           "dont_en": "Do not spray iron mixes blindly",
           "dont_hi": "Bina jaanch iron spray na karein",
           "why_en": "Iron shortage yellows young leaves",
           "why_hi": "Lohe ki kami se nayi patti peeli padti hai"},
    "Mn": {"do_en": "Include manganese in next soil test discussion",
           "do_hi": "Agli jaanch me manganese par charcha karein",
           "dont_en": "Do not mix micronutrients yourself",
           "dont_hi": "Sookshm poshak khud na milayein",
           "why_en": "Manganese helps photosynthesis",
           "why_hi": "Manganese prakash-sanshleshan me sahayak hai"},
    "Cu": {"do_en": "Mention copper in next lab test",
           "do_hi": "Agli lab jaanch me tamba (copper) likhwayein",
           "dont_en": "Do not use copper fungicides as nutrition",
           "dont_hi": "Poshan ke liye copper phaphundi-naashak na samjhein",
           "why_en": "Copper needed in tiny amounts only",
           "why_hi": "Tamba keval bahut thodi matra me chahiye"},
    "CEC": {"do_en": "Build organic matter to hold nutrients better",
           "do_hi": "Poshak rokne ke liye jeevansh badhayein",
           "dont_en": "Do not expect quick fix; it builds slowly",
           "dont_hi": "Turant sudhaar ki aasha na karein; dheere banta hai",
           "why_en": "Better holding capacity means less nutrient loss",
           "why_hi": "Achchi dharan kshamta se poshak kam behta hai"},
}

HEALTHY_TARGET = {  # model counterfactual targets (mid-healthy, not doses)
    "Zn": 1.2, "Organic_Carbon": 0.7, "Available_K": 220.0, "Available_P": 18.0,
    "Total_Nitrogen": 300.0, "Fe": 10.0, "Mn": 5.0, "Cu": 1.5,
    "Pathogen_Load_Index": 0.25, "EC": 0.4, "Soil_Moisture": 20.0, "CEC": 16.0, "pH": 7.0,
}


def _target(feature: str, value: float) -> float:
    if feature == "pH":
        if value > 7.5: return 7.0
        if value < 6.0: return 6.5
        return value
    return HEALTHY_TARGET.get(feature, value)


@dataclass
class Scenario:
    label_en: str
    label_hi: str
    changed: List[str]
    predicted_yield: float
    gain_kg: float
    gain_pct: float


def build_personalized_plan(
    sample: Dict[str, float],
    limiting_features_ranked: List[str],
    predict_yield: Callable[[Dict[str, float]], float],
    top_n: int = 3,
) -> Dict[str, Any]:
    """Counterfactual: baseline vs fixing top-N critical factors one-by-one + combined."""
    baseline = float(predict_yield(dict(sample)))
    top = [f for f in limiting_features_ranked if f in HEALTHY_TARGET or f == "pH"][:top_n]
    scenarios: List[Scenario] = [Scenario("Current soil (as tested)", "Vartamaan mitti (jaanch anusaar)",
                                          [], round(baseline, 2), 0.0, 0.0)]
    for f in top:
        mod = dict(sample); mod[f] = _target(f, float(sample.get(f, 0)))
        y = float(predict_yield(mod)); g = y - baseline
        w = EASY_WORDS.get(f, {})
        scenarios.append(Scenario(f"If {f} improves", f"Agar {f} sudhre",
                                  [f], round(y, 2), round(g, 2),
                                  round(g / y * 100, 1) if y else 0.0))
    if top:
        mod = dict(sample)
        for f in top: mod[f] = _target(f, float(sample.get(f, 0)))
        y = float(predict_yield(mod)); g = y - baseline
        scenarios.append(Scenario(f"If top {len(top)} improve together",
                                  f"Agar sheersh {len(top)} ek saath sudhre",
                                  list(top), round(y, 2), round(g, 2),
                                  round(g / y * 100, 1) if y else 0.0))
    rows = []
    for s in scenarios:
        rows.append({"step_en": s.label_en, "step_hi": s.label_hi,
                     "changed": ", ".join(s.changed) if s.changed else "—",
                     "predicted_yield": s.predicted_yield, "gain_kg": s.gain_kg,
                     "gain_pct": s.gain_pct})
    return {"baseline": round(baseline, 2), "top_factors": top,
            "scenarios": rows, "disclaimer_en": DISCLAIMER_EN, "disclaimer_hi": DISCLAIMER_HI}


def do_dont_table(top_factors: List[str]) -> List[Dict[str, str]]:
    rows = []
    for f in top_factors:
        w = EASY_WORDS.get(f, {"do_en": "Discuss with agronomist", "do_hi": "Vigyani se charcha karein",
                               "dont_en": "Do not act blindly", "dont_hi": "Bina jaanch kadam na uthayein",
                               "why_en": "", "why_hi": ""})
        rows.append({"Factor": f, "✅ Do (EN)": w["do_en"], "✅ करें (HI)": w["do_hi"],
                     "❌ Don't (EN)": w["dont_en"], "❌ न करें (HI)": w["dont_hi"],
                     "Why (EN)": w.get("why_en", ""), "क्यों (HI)": w.get("why_hi", "")})
    return rows


def plot_growth_chart(scenarios: List[Dict[str, Any]], out_png: str | Path) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [s["step_en"] for s in scenarios]
    gains = [s["gain_kg"] for s in scenarios]
    colors = ["grey"] + ["green"] * (len(gains) - 1)
    plt.figure(figsize=(9, 4.2))
    bars = plt.bar(range(len(gains)), gains, color=colors)
    plt.xticks(range(len(labels)), labels, rotation=18, ha="right", fontsize=8)
    plt.ylabel("Extra yield vs today (kg/tree) — model estimate")
    plt.title("What may grow if these improve? (model estimate, not promise)")
    for b, g in zip(bars, gains):
        plt.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{g:+.2f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150)
    plt.close()
    return str(out_png)
