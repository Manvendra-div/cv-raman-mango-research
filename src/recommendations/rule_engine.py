"""Rule engine — triggers on MEASURED values vs thresholds. Never on SHAP alone; never prescribes doses."""
from __future__ import annotations
import json
from pathlib import Path
from src.recommendations.reference_ranges import lookup
_RULES = json.loads(Path(__file__).with_name("agronomic_rules.json").read_text())["rules"]
def _fires(rule_id: str, v: float) -> bool:
    return {"ZN_LOW": v < 0.6, "OC_LOW": v < 0.5, "PH_HIGH": v > 7.5, "PATH_HIGH": v > 0.5, "K_LOW": v < 150}.get(rule_id, False)
def evaluate(sample: dict) -> list[dict]:
    out = []
    for r in _RULES:
        f = r["feature"]
        if f not in sample or sample[f] is None: continue
        try: v = float(sample[f])
        except (TypeError, ValueError): continue
        if _fires(r["id"], v):
            ref = lookup(f)
            out.append({"rule_id": r["id"], "target": "Overall", "feature": f, "feature_value": v,
                "condition": r["condition"], "finding": r["finding"], "recommendation": r["action"],
                "reference": ref, "confidence": r["confidence"], "follow_up": r["follow_up"],
                "xai_support": "Rule fired on measured value; SHAP may corroborate but is not the trigger.",
                "caveat": "Evidence-informed suggestion, not proven yield-gain guarantee. Synthetic-data prototype."})
    if not out:
        out.append({"rule_id": "NO_RULE_TRIGGERED", "target": "Overall", "feature": "", "feature_value": None,
            "condition": "No threshold triggered", "finding": "No actionable threshold crossed.",
            "recommendation": "Maintain monitoring; validate with soil tests.", "confidence": "n/a", "follow_up": "Routine retest.",
            "xai_support": "None", "caveat": "Synthetic prototype."})
    return out
