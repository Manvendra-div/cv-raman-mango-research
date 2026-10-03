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
                payload[feature] = columns[index % 2].number_input(
                    feature,
                    min_value=float(info["min"]),
                    max_value=float(info["max"]),
                    value=min(max(default, float(info["min"])), float(info["max"])),
                    step=float(step),
                    format="%.6f",
                )

    with tabs[3]:
        cat_cols = st.columns(2)
        for index, feature in enumerate(metadata["required_categorical_features"]):
            options = categories[feature]
            default = default_input.get(feature, options[0])
            payload[feature] = cat_cols[index % 2].selectbox(
                feature,
                options,
                index=options.index(default) if default in options else 0,
            )

    return payload


def render_prediction(result: dict[str, Any]) -> None:
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

    st.subheader("Feature Contributions")
    target = st.selectbox("Target", ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"])
    contribution_df = pd.DataFrame(result["explanations"][target])
    st.bar_chart(contribution_df.set_index("feature")["importance"])
    st.dataframe(contribution_df, use_container_width=True, hide_index=True)

    st.subheader("Recommendations")
    recommendations = pd.DataFrame(result["recommendations"])
    st.dataframe(recommendations, use_container_width=True, hide_index=True)

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

    if st.sidebar.button("Run Prediction", type="primary"):
        with st.spinner("Running DSS prediction"):
            try:
                result = api_post("/predict", payload)
            except Exception:
                from src.dss.service import get_service

                result = get_service().predict(payload)
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
