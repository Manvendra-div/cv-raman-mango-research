"""Streamlit frontend for the Phase 9 decision support system."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
API_URL = os.environ.get("DSS_API_URL", "http://127.0.0.1:8000").rstrip("/")


def api_get(path: str) -> dict[str, Any]:
    response = requests.get(f"{API_URL}{path}", timeout=15)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def load_metadata() -> dict[str, Any]:
    try:
        return api_get("/metadata")
    except Exception:
        from src.dss.service import get_service

        return get_service().metadata()


def build_payload(metadata: dict[str, Any]) -> dict[str, Any]:
    default_input = metadata["default_input"]
    ranges = metadata["numeric_ranges"]
    categories = metadata["categorical_options"]

    st.sidebar.header("Orchard Input")
    # Preset buttons: minimum for every parameter vs defaults
    btn_min = st.sidebar.button("Load minimum for every parameter")
    btn_default = st.sidebar.button("Reset to defaults")
    if btn_min:
        for _f, _info in ranges.items():
            st.session_state[f"num_{_f}"] = float(_info["min"])
        for _f in metadata["required_categorical_features"]:
            _opts = categories[_f]
            st.session_state[f"cat_{_f}"] = _opts[0]
        st.session_state.pop("last_result", None)
        st.rerun()
    if btn_default:
        for _f, _info in ranges.items():
            _d = default_input.get(_f, _info["median"])
            st.session_state[f"num_{_f}"] = float(min(max(float(_d), float(_info["min"])), float(_info["max"])))
        for _f in metadata["required_categorical_features"]:
            _opts = categories[_f]
            _d = default_input.get(_f, _opts[0])
            st.session_state[f"cat_{_f}"] = _d if _d in _opts else _opts[0]
        st.session_state.pop("last_result", None)
        st.rerun()
    sample_id = st.sidebar.text_input("Sample ID", value=str(default_input.get("Sample_ID", "DSS-example")))

    payload: dict[str, Any] = {"Sample_ID": sample_id}

    tabs = st.tabs(["Soil", "Microbiome", "Climate", "Orchard"])

    soil_features = [
        "Soil_Health_Index_Phase6",
        "Soil_Chemical_Fertility_Score_Phase6",
        "Soil_Physical_Condition_Score_Phase6",
        "NPK_Balance_Score_Phase6",
        "Micronutrient_Balance_Score_Phase6",
        "Available_P",
        "Available_K",
        "Total_Nitrogen",
        "Organic_Carbon",
        "pH",
        "EC",
        "Mn",
        "Nutrient_Balance_Ratio",
        "Soil_Health_Index",
    ]
    microbiome_features = [
        "Diversity_Score_Phase6",
        "Beneficial_Microbial_Index_Phase6",
        "Pathogen_Load_Index_Phase6",
        "Biocontrol_Index_Phase6",
        "Nutrient_Cycling_Index_Phase6",
        "Pathogen_Beneficial_Ratio_Phase6",
        "Pathogen_Load_Index",
        "Microbial_Richness_Score",
        "Shannon_Index",
        "Pielou_Evenness",
        "Simpson_Index",
        "Richness_Evenness_Balance_Phase6",
        "Trichoderma",
        "Pseudomonas_PGPR",
        "Mycorrhizae_AMF",
        "Euryarchaeota",
        "Fusarium",
    ]
    climate_features = ["Climate_Comfort_Score_Phase6", "Rainfall", "Air_Temp_Avg"]
    orchard_features = ["Tree_Age"]

    groups = [
        (tabs[0], soil_features),
        (tabs[1], microbiome_features),
        (tabs[2], climate_features),
        (tabs[3], orchard_features),
    ]

    for tab, features in groups:
        with tab:
            columns = st.columns(2)
            for index, feature in enumerate(features):
                if feature not in ranges:
                    continue
                info = ranges[feature]
                default = float(default_input.get(feature, info["median"]))
                step = max((info["max"] - info["min"]) / 100.0, 0.0001)
                key = f"num_{feature}"
                init_val = min(max(default, float(info["min"])), float(info["max"]))
                if key not in st.session_state:
                    st.session_state[key] = init_val
                payload[feature] = columns[index % 2].number_input(
                    feature,
                    min_value=float(info["min"]),
                    max_value=float(info["max"]),
                    value=float(st.session_state[key]),
                    step=float(step),
                    format="%.6f",
                    key=key,
                )

    with tabs[3]:
        cat_cols = st.columns(2)
        for index, feature in enumerate(metadata["required_categorical_features"]):
            options = categories[feature]
            default = default_input.get(feature, options[0])
            key = f"cat_{feature}"
            if key not in st.session_state:
                st.session_state[key] = default if default in options else options[0]
            idx = options.index(st.session_state[key]) if st.session_state[key] in options else 0
            payload[feature] = cat_cols[index % 2].selectbox(
                feature,
                options,
                index=idx,
                key=key,
            )

    return payload


def render_zone_analysis(zone_data: dict[str, Any], predicted_yield: float) -> None:
    """Render zone intelligence widgets."""
    st.subheader("🌍 Zone Intelligence & Benchmarking")

    # Comparable orchards summary
    comp = zone_data["comparable_orchards"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Comparable Orchards", comp["orchard_count"])
    col2.metric("Sample Count", comp["sample_count"])
    col3.metric("Match Quality", "✓ Sufficient" if comp["sufficient"] else "⚠ Limited")

    if comp["warnings"]:
        st.info(f"Matching: {'; '.join(comp['warnings'])}")

    # Yield gap analysis
    gap = zone_data["yield_gap"]["primary"]
    ref = zone_data["reference_yield"]

    st.subheader("📊 Yield Gap Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Predicted", f"{predicted_yield:.1f} kg/tree")
    col2.metric("Zone Q75", f"{ref['q75']:.1f} kg/tree")
    col3.metric("Gap", f"{gap['gap_absolute_kg']:.1f} kg/tree",
                delta=f"{gap['gap_percentage']:.1f}%", delta_color="inverse")
    col4.metric("Top 10%", f"{ref['top10_mean']:.1f} kg/tree")

    st.caption(gap["interpretation"])

    # Limiting factors
    factors = zone_data.get("limiting_factors", [])
    if factors:
        st.subheader("⚠️ Limiting Factors")
        factors_df = pd.DataFrame(factors)
        display_cols = ["feature", "measured_value", "confidence", "severity_score", "recommendation"]
        st.dataframe(
            factors_df[display_cols].head(5),
            use_container_width=True,
            hide_index=True,
        )


def render_farmer_explainer(result: dict[str, Any], payload: dict[str, Any]) -> None:
    """Personalized easy-words Do/Don't + what-if growth visuals (EN+HI)."""
    from src.recommendations.personalized_explainer import (
        build_personalized_plan, do_dont_table, plot_growth_chart,
        DISCLAIMER_EN, DISCLAIMER_HI,
    )
    st.subheader("🧑‍🌾 Farmer Explainer — Easy Words / आसान भाषा")
    zone = result.get("zone_intelligence", {})
    factors = zone.get("limiting_factors", []) if isinstance(zone, dict) else []
    ranked = [f["feature"] for f in factors if isinstance(f, dict) and "feature" in f][:5]
    if not ranked:  # fallback: worst measured vs reference
        ranked = ["Zn", "Organic_Carbon", "Pathogen_Load_Index", "Available_K", "pH"]
    try:
        from src.dss.service import get_service
        svc = get_service()

        def _py(sample: dict[str, Any]) -> float:
            d = dict(payload)
            d.update({k: sample.get(k, d.get(k)) for k in sample})
            return float(svc.predict(d)["predictions"]["Mango_Yield"]["value"])

        plan = build_personalized_plan(dict(payload), ranked, _py, top_n=3)
    except Exception as e:
        st.warning(f"Personalized estimate unavailable: {e}")
        return
    st.markdown(f"**Top focus for YOUR orchard:** {', '.join(plan['top_factors']) or '—'}")
    st.dataframe(do_dont_table(plan["top_factors"]), use_container_width=True, hide_index=True)
    chart_df = pd.DataFrame(plan["scenarios"])[["step_en", "gain_kg"]]
    st.bar_chart(chart_df.set_index("step_en"))
    st.dataframe(pd.DataFrame(plan["scenarios"]), use_container_width=True, hide_index=True)
    try:
        png = plot_growth_chart(plan["scenarios"], "reports/figures/farmer_growth_plan.png")
        st.image(png, caption="Model-estimated extra yield if these improve (not a promise)")
    except Exception:
        pass
    st.caption(f"⚠️ {DISCLAIMER_EN}")
    st.caption(f"⚠️ {DISCLAIMER_HI}")


def render_prediction(result: dict[str, Any]) -> None:
    if "predictions" not in result:
        st.error(
            "Prediction payload missing 'predictions' key. "
            f"Got keys: {list(result.keys())}. Check API /predict vs /zone-analysis shape."
        )
        st.json({k: (str(v)[:500]) for k, v in result.items()})
        return
    predictions = result["predictions"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Mango Yield", f"{predictions['Mango_Yield']['value']:.2f} kg/tree")
    col2.metric(
        "Disease Risk",
        predictions["Disease_Risk"]["class"],
        f"{predictions['Disease_Risk']['confidence']:.1%} confidence",
    )
    col3.metric(
        "Nutrient Status",
        predictions["Nutrient_Availability"]["class"],
        f"{predictions['Nutrient_Availability']['confidence']:.1%} confidence",
    )

    # Zone Intelligence (if available)
    if "zone_intelligence" in result:
        render_zone_analysis(
            result["zone_intelligence"],
            predictions['Mango_Yield']['value']
        )

    st.subheader("Feature Contributions")
    target = st.selectbox("Target", ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"])
    contribution_df = pd.DataFrame(result["explanations"][target])
    st.bar_chart(contribution_df.set_index("feature")["importance"])
    st.dataframe(contribution_df, use_container_width=True, hide_index=True)

    st.subheader("Recommendations")
    recommendations = pd.DataFrame(result["recommendations"])
    st.dataframe(recommendations, use_container_width=True, hide_index=True)

    render_farmer_explainer(result, result.get("input_payload", {}))

    try:
        markdown_report = api_post("/report", result["input_payload"])["markdown_report"]
    except Exception:
        from src.dss.service import get_service

        markdown_report = get_service().export_markdown_report(result)
    st.download_button(
        "Download Markdown Report",
        data=markdown_report,
        file_name=f"{result.get('sample_id') or 'dss'}_prediction_report.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download JSON",
        data=json.dumps(result, indent=2),
        file_name=f"{result.get('sample_id') or 'dss'}_prediction.json",
        mime="application/json",
    )


def main() -> None:
    st.set_page_config(
        page_title="Mango Soil Microbiome DSS",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Mango Soil Microbiome DSS")

    metadata = load_metadata()
    payload = build_payload(metadata)

    enable_zone = st.sidebar.checkbox("Enable Zone Intelligence", value=True)

    if st.sidebar.button("Run Prediction", type="primary"):
        with st.spinner("Running DSS prediction"):
            try:
                # Always get base prediction first (/predict shape has "predictions").
                result = api_post("/predict", payload)
                if enable_zone:
                    try:
                        zone_resp = api_post("/zone-analysis", payload)
                        # /zone-analysis returns {sample_id, predicted_yield, zone_intelligence}
                        if isinstance(zone_resp, dict) and "zone_intelligence" in zone_resp:
                            result["zone_intelligence"] = zone_resp["zone_intelligence"]
                    except Exception as zone_err:
                        st.warning(f"Zone analysis unavailable: {zone_err}")
            except Exception:
                from src.dss.service import get_service
                from src.dss.zone_service import get_zone_service

                result = get_service().predict(payload)

                if enable_zone:
                    zone_svc = get_zone_service()
                    zone_result = zone_svc.zone_analysis(
                        predicted_yield=result["predictions"]["Mango_Yield"]["value"],
                        village=payload["Village"],
                        variety=payload["Mango_Variety"],
                        tree_age=payload["Tree_Age"],
                        management=payload.get("Management"),
                        sample_values=get_service().input_to_payload(payload),
                        shap_contributions=result["explanations"].get("shap_values"),
                    )
                    result["zone_intelligence"] = zone_result

            result["input_payload"] = payload
            st.session_state["last_result"] = result

    if "last_result" not in st.session_state:
        result = api_post("/predict", payload) if os.environ.get("DSS_AUTORUN_API", "0") == "1" else None
    else:
        result = st.session_state["last_result"]

    if result:
        render_prediction(result)
    else:
        st.info("Enter orchard inputs in the tabs and run a prediction.")


if __name__ == "__main__":
    main()
