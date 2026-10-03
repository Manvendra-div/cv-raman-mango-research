"""Streamlit research dashboard for the mango soil microbiome project."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    alt.data_transformers.disable_max_rows()
except Exception:
    pass


FEATURE_TABLE = "data/processed/feature_table.csv"
SELECTED_FEATURES = "data/processed/selected_features.json"
PHASE6_SUMMARY = "outputs/feature_engineering/phase6_feature_summary.json"
PHASE7_CHAMPIONS = "outputs/metrics/phase7_model_results/phase7_champion_summary.csv"
PHASE7_HOLDOUT = "outputs/metrics/phase7_model_results/phase7_rahimabad_holdout_summary.csv"
REGRESSION_METRICS = "outputs/metrics/regression/regression_model_metrics.csv"
CLASSIFICATION_METRICS = "outputs/metrics/classification/classification_model_metrics.csv"
REGRESSION_VILLAGE_ERROR = "outputs/metrics/regression/regression_village_wise_error.csv"
REGRESSION_SEASON_ERROR = "outputs/metrics/regression/regression_season_wise_error.csv"
GLOBAL_IMPORTANCE = "outputs/explainability/phase8_xai/tables/phase8_global_feature_importance.csv"
RECOMMENDATION_RULES = "outputs/explainability/phase8_xai/tables/phase8_recommendation_rules.csv"
INSTANCE_RECOMMENDATIONS = "outputs/explainability/phase8_xai/tables/phase8_instance_recommendations.csv"
PHASE10_SUMMARY = "outputs/validation/phase10/phase10_validation_summary.json"
PHASE10_INTERNAL_SUMMARY = "outputs/validation/phase10/phase10_internal_cv_summary.csv"
PHASE10_GEO_REGRESSION = "outputs/validation/phase10/phase10_geographic_holdout_regression_metrics.csv"
PHASE10_GEO_CLASSIFICATION = "outputs/validation/phase10/phase10_geographic_holdout_classification_metrics.csv"
PHASE10_INTERNAL_VS_GEO = "outputs/validation/phase10/phase10_internal_vs_geographic_summary.csv"
PHASE10_REAL_STATUS = "outputs/validation/phase10/phase10_real_sample_validation_status.csv"
PHASE10_FIELD_STATUS = "outputs/validation/phase10/phase10_field_intervention_status.csv"
PHASE10_MANIFEST = "outputs/validation/phase10/phase10_validation_manifest.csv"

TARGETS = ["Mango_Yield", "Disease_Risk", "Nutrient_Availability"]
TARGET_SLUGS = {
    "Mango_Yield": "mango_yield",
    "Disease_Risk": "disease_risk",
    "Nutrient_Availability": "nutrient_availability",
}
PALETTE = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"]


def project_path(relative: str | Path) -> Path:
    return PROJECT_ROOT / relative


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


@st.cache_data(show_spinner=False)
def read_csv(relative: str) -> pd.DataFrame:
    path = project_path(relative)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def read_json(relative: str) -> dict[str, Any]:
    path = project_path(relative)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def load_dss_service() -> Any:
    from src.dss.service import get_service

    return get_service()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.1rem;
            padding-bottom: 2rem;
            max-width: 1420px;
        }
        h1, h2, h3, h4, p, label {
            letter-spacing: 0;
        }
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
        }
        [data-testid="stMetricLabel"] p {
            color: #475569;
            font-size: 0.82rem;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }
        section[data-testid="stSidebar"] {
            background: #f8fafc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_number(value: Any, digits: int = 2, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, str):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(numeric) >= 1000:
        text = f"{numeric:,.0f}" if numeric.is_integer() else f"{numeric:,.{digits}f}"
    else:
        text = f"{numeric:.{digits}f}" if not numeric.is_integer() else f"{numeric:.0f}"
    return f"{text}{suffix}"


def metric_grid(items: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        col.metric(label, value, delta=delta)


def show_table(df: pd.DataFrame, columns: list[str] | None = None, height: int | None = None) -> None:
    if df.empty:
        st.info("No rows available.")
        return
    view = df[columns].copy() if columns else df.copy()
    numeric = view.select_dtypes(include="number").columns
    view[numeric] = view[numeric].round(4)
    dataframe_args: dict[str, Any] = {"width": "stretch", "hide_index": True}
    if height is not None:
        dataframe_args["height"] = height
    st.dataframe(view, **dataframe_args)


def chart_properties(height: int, title: str | None = None) -> dict[str, Any]:
    props: dict[str, Any] = {"height": height}
    if title:
        props["title"] = title
    return props


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str | None = None,
    height: int = 290,
    sort: str | list[str] | None = None,
) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No chart data available.")
        return
    enc: dict[str, Any] = {
        "x": alt.X(f"{x}:N", sort=sort, axis=alt.Axis(labelAngle=-30), title=x.replace("_", " ")),
        "y": alt.Y(f"{y}:Q", title=y.replace("_", " ")),
        "tooltip": [col for col in df.columns if col in {x, y, color, "Rows", "Count", "Target", "Model", "Split"}],
    }
    if color:
        enc["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=PALETTE), title=color.replace("_", " "))
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(**enc)
        .properties(**chart_properties(height, title))
    )
    st.altair_chart(chart, width="stretch")


def horizontal_bar(
    df: pd.DataFrame,
    label: str,
    value: str,
    color: str | None = None,
    title: str | None = None,
    height: int = 360,
) -> None:
    if df.empty or label not in df.columns or value not in df.columns:
        st.info("No chart data available.")
        return
    enc: dict[str, Any] = {
        "x": alt.X(f"{value}:Q", title=value.replace("_", " ")),
        "y": alt.Y(f"{label}:N", sort="-x", title=None),
        "tooltip": [col for col in df.columns if col in {label, value, color, "Rank", "Target"}],
    }
    if color:
        enc["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=PALETTE), title=color.replace("_", " "))
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=2, cornerRadiusBottomRight=2)
        .encode(**enc)
        .properties(**chart_properties(height, title))
    )
    st.altair_chart(chart, width="stretch")


def histogram(df: pd.DataFrame, field: str, title: str | None = None) -> None:
    if df.empty or field not in df.columns:
        st.info("No chart data available.")
        return
    chart_df = df[[field]].dropna()
    chart = (
        alt.Chart(chart_df)
        .mark_bar(color="#2563eb", cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{field}:Q", bin=alt.Bin(maxbins=36), title=field.replace("_", " ")),
            y=alt.Y("count():Q", title="Rows"),
            tooltip=[alt.Tooltip("count():Q", title="Rows")],
        )
        .properties(**chart_properties(300, title))
    )
    st.altair_chart(chart, width="stretch")


def scatter(df: pd.DataFrame, x: str, y: str, color: str = "Village") -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No chart data available.")
        return
    chart_df = df[[x, y, color, "Sample_ID"]].dropna()
    if len(chart_df) > 3000:
        chart_df = chart_df.sample(3000, random_state=42)
    chart = (
        alt.Chart(chart_df)
        .mark_circle(size=36, opacity=0.55)
        .encode(
            x=alt.X(f"{x}:Q", title=x.replace("_", " ")),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ")),
            color=alt.Color(f"{color}:N", scale=alt.Scale(range=PALETTE), title=color),
            tooltip=["Sample_ID", color, x, y],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, width="stretch")


def load_main_data() -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    return read_csv(FEATURE_TABLE), read_json(SELECTED_FEATURES), read_json(PHASE6_SUMMARY)


def phase_rows() -> pd.DataFrame:
    checks = [
        ("Phase 1", "Literature review", "phase_1_literature_review"),
        ("Phase 2", "Study design and sampling", "phase_2_study_design_sampling_framework"),
        ("Phase 3", "Data collection", "phase_3_soil_microbiome_data_collection"),
        ("Phase 4", "Laboratory analysis", "phase_4_laboratory_analysis"),
        ("Phase 5", "Preprocessing", "outputs/reports/phase5_preprocessing/preprocessing_report.md"),
        ("Phase 6", "Feature engineering", "outputs/reports/phase6_feature_engineering/feature_selection_report.md"),
        ("Phase 7", "Model development", "outputs/reports/phase7_model_results/phase7_complete_model_results_report.md"),
        ("Phase 8", "Explainable AI", "outputs/reports/phase8_explainable_ai/phase8_explainable_ai_report.md"),
        ("Phase 9", "Decision support system", "src/dss/dashboard.py"),
        ("Phase 10", "Validation", "outputs/reports/phase10_validation/phase10_validation_report.md"),
    ]
    rows = []
    for phase, label, evidence in checks:
        exists = project_path(evidence).exists()
        rows.append({"Phase": phase, "Area": label, "Status": "Available" if exists else "Missing", "Evidence": evidence})
    return pd.DataFrame(rows)


def page_overview() -> None:
    df, selected, phase6 = load_main_data()
    champions = read_csv(PHASE7_CHAMPIONS)
    phase10 = read_json(PHASE10_SUMMARY)

    st.subheader("Research Snapshot")
    selected_numeric = selected.get("selected_numeric_features", [])
    selected_categorical = selected.get("categorical_features_for_encoding", [])
    villages = df["Village"].nunique() if "Village" in df else 0
    holdout_rows = int((df["Village"] == "Rahimabad").sum()) if "Village" in df else phase10.get("rahimabad_rows", 0)
    metric_grid(
        [
            ("Samples", format_number(len(df), 0), None),
            ("Villages", format_number(villages, 0), None),
            ("Selected Features", format_number(len(selected_numeric) + len(selected_categorical), 0), None),
            ("Rahimabad Hold-Out", format_number(holdout_rows, 0), None),
        ]
    )

    left, right = st.columns([1.05, 1])
    with left:
        if "Split" in df:
            split_counts = df["Split"].value_counts().rename_axis("Split").reset_index(name="Rows")
            bar_chart(split_counts, "Split", "Rows", title="Dataset Splits", height=260)
        st.markdown("#### Pipeline Coverage")
        show_table(phase_rows(), height=390)
    with right:
        st.markdown("#### Champion Models")
        show_table(champions)
        st.markdown("#### Phase 10 Summary")
        metric_grid(
            [
                (
                    "Best Yield RMSE",
                    format_number(phase10.get("best_internal_regression_model", {}).get("mean_rmse"), 3),
                    phase10.get("best_internal_regression_model", {}).get("model"),
                ),
                (
                    "Disease Macro F1",
                    format_number(
                        phase10.get("best_internal_classification_models", {})
                        .get("Disease_Risk", {})
                        .get("mean_macro_f1"),
                        4,
                    ),
                    phase10.get("best_internal_classification_models", {}).get("Disease_Risk", {}).get("model"),
                ),
                (
                    "Nutrient Macro F1",
                    format_number(
                        phase10.get("best_internal_classification_models", {})
                        .get("Nutrient_Availability", {})
                        .get("mean_macro_f1"),
                        4,
                    ),
                    phase10.get("best_internal_classification_models", {}).get("Nutrient_Availability", {}).get("model"),
                ),
            ]
        )

    st.markdown("#### Target Distributions")
    col1, col2, col3 = st.columns(3)
    with col1:
        histogram(df, "Mango_Yield", "Mango Yield")
    with col2:
        if "Disease_Risk" in df:
            bar_chart(df["Disease_Risk"].value_counts().rename_axis("Disease_Risk").reset_index(name="Rows"), "Disease_Risk", "Rows")
    with col3:
        if "Nutrient_Availability" in df:
            bar_chart(
                df["Nutrient_Availability"].value_counts().rename_axis("Nutrient_Availability").reset_index(name="Rows"),
                "Nutrient_Availability",
                "Rows",
            )

    st.markdown("#### Feature Engineering Summary")
    phase6_rows = [
        ("Engineered Phase 6 Features", phase6.get("phase6_feature_count")),
        ("Candidate Numeric Features", phase6.get("candidate_numeric_feature_count")),
        ("Selected Numeric Features", phase6.get("selected_numeric_feature_count")),
        ("High-Correlation Redundancy Pairs", phase6.get("redundancy_pairs_abs_corr_ge_0_90")),
    ]
    metric_grid([(label, format_number(value, 0), None) for label, value in phase6_rows])


def filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    with st.expander("Filters", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        village = c1.multiselect("Village", sorted(df["Village"].dropna().unique()), default=sorted(df["Village"].dropna().unique()))
        split = c2.multiselect("Split", sorted(df["Split"].dropna().unique()), default=sorted(df["Split"].dropna().unique()))
        variety = c3.multiselect(
            "Variety",
            sorted(df["Mango_Variety"].dropna().unique()),
            default=sorted(df["Mango_Variety"].dropna().unique()),
        )
        season = c4.multiselect(
            "Season",
            sorted(df["Sampling_Season"].dropna().unique()),
            default=sorted(df["Sampling_Season"].dropna().unique()),
        )
        management = c5.multiselect(
            "Management",
            sorted(df["Management"].dropna().unique()),
            default=sorted(df["Management"].dropna().unique()),
        )
    mask = (
        df["Village"].isin(village)
        & df["Split"].isin(split)
        & df["Mango_Variety"].isin(variety)
        & df["Sampling_Season"].isin(season)
        & df["Management"].isin(management)
    )
    return df[mask].copy()


def page_data_explorer() -> None:
    df, selected, _ = load_main_data()
    st.subheader("Dataset Explorer")
    view = filtered_data(df)
    high_disease = (view["Disease_Risk"].astype(str) == "High").mean() * 100 if not view.empty else None
    high_nutrient = (view["Nutrient_Availability"].astype(str) == "High").mean() * 100 if not view.empty else None
    metric_grid(
        [
            ("Filtered Rows", format_number(len(view), 0), None),
            ("Mean Yield", format_number(view["Mango_Yield"].mean() if not view.empty else None, 2, " kg/tree"), None),
            ("High Disease", format_number(high_disease, 1, "%"), None),
            ("High Nutrient", format_number(high_nutrient, 1, "%"), None),
        ]
    )

    left, right = st.columns([1, 1])
    with left:
        if not view.empty:
            by_village = (
                view.groupby("Village", as_index=False)
                .agg(Rows=("Sample_ID", "count"), Mean_Yield=("Mango_Yield", "mean"), Mean_Soil_Health=("Soil_Health_Index_Phase6", "mean"))
                .sort_values("Mean_Yield", ascending=False)
            )
            bar_chart(by_village, "Village", "Mean_Yield", title="Mean Yield by Village", height=310)
    with right:
        numeric_options = selected.get("selected_numeric_features", [])
        field = st.selectbox("Feature Distribution", numeric_options, index=numeric_options.index("Soil_Health_Index_Phase6") if "Soil_Health_Index_Phase6" in numeric_options else 0)
        histogram(view, field, field.replace("_", " "))

    st.markdown("#### Soil Health and Yield")
    x_feature = st.selectbox(
        "X Feature",
        selected.get("selected_numeric_features", []),
        index=selected.get("selected_numeric_features", []).index("Soil_Health_Index_Phase6")
        if "Soil_Health_Index_Phase6" in selected.get("selected_numeric_features", [])
        else 0,
    )
    scatter(view, x_feature, "Mango_Yield")

    st.markdown("#### Aggregates")
    group = st.selectbox("Group By", ["Village", "Mango_Variety", "Sampling_Season", "Management", "Soil_Depth"])
    grouped = (
        view.groupby(group, as_index=False)
        .agg(
            Rows=("Sample_ID", "count"),
            Mean_Yield=("Mango_Yield", "mean"),
            Mean_Soil_Health=("Soil_Health_Index_Phase6", "mean"),
            Mean_Pathogen_Load=("Pathogen_Load_Index_Phase6", "mean"),
            Mean_NPK_Balance=("NPK_Balance_Score_Phase6", "mean"),
        )
        .sort_values("Rows", ascending=False)
        if not view.empty
        else pd.DataFrame()
    )
    show_table(grouped)

    st.markdown("#### Sample Rows")
    columns = [
        "Sample_ID",
        "Orchard_ID",
        "Village",
        "Mango_Variety",
        "Sampling_Season",
        "Management",
        "Mango_Yield",
        "Disease_Risk",
        "Nutrient_Availability",
        "Soil_Health_Index_Phase6",
        "Pathogen_Load_Index_Phase6",
        "NPK_Balance_Score_Phase6",
    ]
    show_table(view[columns].head(500), height=430)


def page_model_performance() -> None:
    st.subheader("Model Performance")
    champions = read_csv(PHASE7_CHAMPIONS)
    holdout = read_csv(PHASE7_HOLDOUT)
    reg = read_csv(REGRESSION_METRICS)
    clf = read_csv(CLASSIFICATION_METRICS)

    st.markdown("#### Champion Selection")
    show_table(champions)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Regression RMSE")
        if not reg.empty and {"Model", "Split", "RMSE"}.issubset(reg.columns):
            chart_df = reg.copy()
            chart_df["Model_Split"] = chart_df["Model"] + " - " + chart_df["Split"].astype(str)
            bar_chart(chart_df, "Model", "RMSE", color="Split", title="Lower is Better", height=360)
        show_table(reg, height=320)
    with col2:
        st.markdown("#### Classification Macro F1")
        if not clf.empty and {"Target", "Model", "Split", "Macro_F1"}.issubset(clf.columns):
            target = st.selectbox("Classification Target", sorted(clf["Target"].dropna().unique()))
            chart_df = clf[clf["Target"] == target].copy()
            bar_chart(chart_df, "Model", "Macro_F1", color="Split", title="Higher is Better", height=360)
            show_table(chart_df, height=320)
        else:
            show_table(clf, height=320)

    st.markdown("#### Rahimabad Hold-Out Summary")
    show_table(holdout)

    village_error = read_csv(REGRESSION_VILLAGE_ERROR)
    season_error = read_csv(REGRESSION_SEASON_ERROR)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Village-Wise Yield Error")
        if not village_error.empty and {"Village", "RMSE"}.issubset(village_error.columns):
            bar_chart(village_error, "Village", "RMSE", title="Regression RMSE by Village")
        show_table(village_error)
    with right:
        st.markdown("#### Season-Wise Yield Error")
        if not season_error.empty and {"Sampling_Season", "RMSE"}.issubset(season_error.columns):
            bar_chart(season_error, "Sampling_Season", "RMSE", title="Regression RMSE by Season")
        show_table(season_error)


def explanation_images(target: str, prefix: str) -> list[Path]:
    slug = TARGET_SLUGS[target]
    folder = project_path("outputs/explainability/phase8_xai/figures")
    local = project_path("outputs/explainability/phase8_xai/local_explanations")
    if prefix == "summary":
        return [folder / f"shap_summary_bar_{slug}.png", folder / f"shap_summary_beeswarm_{slug}.png"]
    if prefix == "dependence":
        return sorted(folder.glob(f"shap_dependence_{slug}_*.png"))
    if prefix == "local":
        return sorted(local.glob(f"shap_waterfall_{slug}_*.png")) + sorted(local.glob(f"lime_{slug}_*.png"))
    return []


def page_explainability() -> None:
    st.subheader("Explainable AI")
    importance = read_csv(GLOBAL_IMPORTANCE)
    rules = read_csv(RECOMMENDATION_RULES)
    instance_rules = read_csv(INSTANCE_RECOMMENDATIONS)

    target = st.selectbox("Target", TARGETS)
    target_imp = importance[
        (importance.get("Target", pd.Series(dtype=str)) == target)
        & (importance.get("Importance_Type", pd.Series(dtype=str)) == "SHAP_Mean_Abs_Aggregated")
    ].copy()
    target_imp = target_imp.sort_values("Rank").head(15) if not target_imp.empty else target_imp

    left, right = st.columns([1, 1])
    with left:
        horizontal_bar(target_imp, "Original_Feature", "Importance", title="Top SHAP Features")
    with right:
        show_table(target_imp[["Rank", "Original_Feature", "Importance", "Mean_SHAP", "Top_Transformed_Feature"]] if not target_imp.empty else target_imp)

    st.markdown("#### SHAP Summary")
    img_cols = st.columns(2)
    for col, image_path in zip(img_cols, explanation_images(target, "summary")):
        with col:
            if image_path.exists():
                st.image(str(image_path), caption=rel(image_path), width="stretch")
            else:
                st.info(f"Missing image: {rel(image_path)}")

    dep_images = explanation_images(target, "dependence")
    local_images = explanation_images(target, "local")
    dep_col, local_col = st.columns(2)
    with dep_col:
        st.markdown("#### Dependence Diagnostics")
        if dep_images:
            selected = st.selectbox("Dependence Plot", dep_images, format_func=lambda p: p.stem)
            st.image(str(selected), caption=rel(selected), width="stretch")
        else:
            st.info("No dependence plots found.")
    with local_col:
        st.markdown("#### Local Explanations")
        if local_images:
            selected = st.selectbox("Local Plot", local_images, format_func=lambda p: p.stem)
            st.image(str(selected), caption=rel(selected), width="stretch")
        else:
            st.info("No local explanation plots found.")

    st.markdown("#### Recommendation Rules")
    show_table(rules)
    st.markdown("#### Instance-Level Recommendation Examples")
    show_table(instance_rules.head(200), height=360)


def page_validation() -> None:
    st.subheader("Validation")
    summary = read_json(PHASE10_SUMMARY)
    internal = read_csv(PHASE10_INTERNAL_SUMMARY)
    geo_reg = read_csv(PHASE10_GEO_REGRESSION)
    geo_clf = read_csv(PHASE10_GEO_CLASSIFICATION)
    internal_vs_geo = read_csv(PHASE10_INTERNAL_VS_GEO)
    real_status = read_csv(PHASE10_REAL_STATUS)
    field_status = read_csv(PHASE10_FIELD_STATUS)

    metric_grid(
        [
            ("Rows Validated", format_number(summary.get("rows"), 0), None),
            ("K-Fold Splits", format_number(summary.get("kfold_splits"), 0), None),
            ("Rahimabad Rows", format_number(summary.get("rahimabad_rows"), 0), None),
            ("Real Samples", summary.get("real_sample_validation_status", "NA"), None),
        ]
    )

    left, right = st.columns(2)
    with left:
        st.markdown("#### Internal Regression CV")
        reg = internal[internal["Task"] == "Regression"].copy() if "Task" in internal else pd.DataFrame()
        if not reg.empty:
            bar_chart(reg, "Model", "Mean_RMSE", title="Mean RMSE by Algorithm")
        show_table(reg)
    with right:
        st.markdown("#### Internal Classification CV")
        clf = internal[internal["Task"] == "Classification"].copy() if "Task" in internal else pd.DataFrame()
        if not clf.empty:
            target = st.selectbox("Validation Classification Target", sorted(clf["Target"].dropna().unique()))
            bar_chart(clf[clf["Target"] == target], "Model", "Mean_Macro_F1", title="Mean Macro F1 by Algorithm")
        show_table(clf)

    st.markdown("#### Rahimabad Geographic Hold-Out")
    h1, h2 = st.columns(2)
    with h1:
        show_table(geo_reg)
    with h2:
        show_table(geo_clf)

    st.markdown("#### Internal vs Geographic")
    if not internal_vs_geo.empty:
        metric = st.selectbox("Comparison Target", sorted(internal_vs_geo["Target"].dropna().unique()))
        chart_df = internal_vs_geo[internal_vs_geo["Target"] == metric].copy()
        long = chart_df.melt(
            id_vars=["Task", "Target", "Model", "Primary_Metric"],
            value_vars=["Internal_CV_Mean", "Geographic_Holdout"],
            var_name="Validation_Level",
            value_name="Metric_Value",
        )
        bar_chart(long, "Model", "Metric_Value", color="Validation_Level", title="Internal CV vs Rahimabad Hold-Out")
        show_table(chart_df)
    else:
        st.info("No comparison rows available.")

    st.markdown("#### Real-Sample and Field-Intervention Status")
    s1, s2 = st.columns(2)
    with s1:
        show_table(real_status)
    with s2:
        show_table(field_status)


def dss_default_from_sample(df: pd.DataFrame, metadata: dict[str, Any]) -> dict[str, Any]:
    base = dict(metadata["default_input"])
    source = st.radio("Input Profile", ["Median profile", "Dataset sample"], horizontal=True)
    if source == "Dataset sample" and not df.empty:
        pool = df.sample(min(500, len(df)), random_state=42).sort_values("Sample_ID")
        sample_id = st.selectbox("Sample", pool["Sample_ID"].tolist())
        row = pool[pool["Sample_ID"] == sample_id].iloc[0].to_dict()
        for key in metadata["required_numeric_features"] + metadata["required_categorical_features"] + ["Fusarium"]:
            if key in row and pd.notna(row[key]):
                base[key] = row[key]
        base["Sample_ID"] = sample_id
    return base


def number_payload_widget(feature: str, default_input: dict[str, Any], ranges: dict[str, Any], key_seed: str) -> float:
    info = ranges[feature]
    min_value = float(info["min"])
    max_value = float(info["max"])
    default = float(default_input.get(feature, info["median"]))
    value = min(max(default, min_value), max_value)
    step = max((max_value - min_value) / 100.0, 0.0001)
    return st.number_input(
        feature,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=float(step),
        format="%.6f",
        key=f"dss_{key_seed}_{feature}",
    )


def build_dss_payload(metadata: dict[str, Any], default_input: dict[str, Any]) -> dict[str, Any]:
    ranges = metadata["numeric_ranges"]
    categories = metadata["categorical_options"]
    key_seed = str(default_input.get("Sample_ID", "median"))
    payload: dict[str, Any] = {"Sample_ID": st.text_input("Sample ID", value=str(default_input.get("Sample_ID", "dashboard-sample")))}

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

    tabs = st.tabs(["Soil", "Microbiome", "Climate", "Orchard"])
    for tab, features in zip(tabs, [soil_features, microbiome_features, climate_features, orchard_features]):
        with tab:
            columns = st.columns(2)
            for index, feature in enumerate(features):
                if feature in ranges:
                    with columns[index % 2]:
                        payload[feature] = number_payload_widget(feature, default_input, ranges, key_seed)

    with tabs[3]:
        cat_cols = st.columns(2)
        for index, feature in enumerate(metadata["required_categorical_features"]):
            options = categories[feature]
            default = default_input.get(feature, options[0])
            with cat_cols[index % 2]:
                payload[feature] = st.selectbox(
                    feature,
                    options,
                    index=options.index(default) if default in options else 0,
                    key=f"dss_{key_seed}_{feature}",
                )
    return payload


def render_dss_result(result: dict[str, Any], service: Any) -> None:
    predictions = result["predictions"]
    metric_grid(
        [
            ("Mango Yield", format_number(predictions["Mango_Yield"]["value"], 2, " kg/tree"), predictions["Mango_Yield"]["model"]),
            (
                "Disease Risk",
                predictions["Disease_Risk"]["class"],
                f"{predictions['Disease_Risk']['confidence']:.1%} confidence",
            ),
            (
                "Nutrient Status",
                predictions["Nutrient_Availability"]["class"],
                f"{predictions['Nutrient_Availability']['confidence']:.1%} confidence",
            ),
        ]
    )

    prob_rows = []
    for target in ["Disease_Risk", "Nutrient_Availability"]:
        for label, probability in predictions[target]["probabilities"].items():
            prob_rows.append({"Target": target, "Class": label, "Probability": probability})
    st.markdown("#### Class Probabilities")
    bar_chart(pd.DataFrame(prob_rows), "Class", "Probability", color="Target", height=250)

    st.markdown("#### Feature Contributions")
    target = st.selectbox("Explanation Target", TARGETS)
    contribution_df = pd.DataFrame(result["explanations"][target])
    horizontal_bar(contribution_df, "feature", "importance", title=target)
    show_table(contribution_df)

    st.markdown("#### Recommendations")
    recommendations = pd.DataFrame(result["recommendations"])
    show_table(recommendations)

    col1, col2 = st.columns(2)
    col1.download_button(
        "Download JSON",
        data=json.dumps(result, indent=2),
        file_name=f"{result.get('sample_id') or 'dashboard'}_prediction.json",
        mime="application/json",
    )
    col2.download_button(
        "Download Markdown Report",
        data=service.export_markdown_report(result),
        file_name=f"{result.get('sample_id') or 'dashboard'}_prediction_report.md",
        mime="text/markdown",
    )


def page_decision_support() -> None:
    st.subheader("Decision Support")
    df, _, _ = load_main_data()
    with st.spinner("Loading champion models"):
        service = load_dss_service()
    metadata = service.metadata()
    default_input = dss_default_from_sample(df, metadata)
    payload = build_dss_payload(metadata, default_input)

    if st.button("Run Prediction", type="primary"):
        with st.spinner("Running champion models"):
            result = service.predict(payload)
            st.session_state["research_dashboard_prediction"] = result

    if "research_dashboard_prediction" in st.session_state:
        render_dss_result(st.session_state["research_dashboard_prediction"], service)
    else:
        st.info("Run a prediction to view model output, explanations, and recommendations.")


def artifact_inventory() -> pd.DataFrame:
    direct_paths = [
        FEATURE_TABLE,
        SELECTED_FEATURES,
        PHASE6_SUMMARY,
        PHASE7_CHAMPIONS,
        PHASE7_HOLDOUT,
        GLOBAL_IMPORTANCE,
        RECOMMENDATION_RULES,
        PHASE10_SUMMARY,
        PHASE10_MANIFEST,
        "outputs/reports/phase6_feature_engineering/feature_selection_report.md",
        "outputs/reports/phase7_model_results/phase7_complete_model_results_report.md",
        "outputs/reports/phase8_explainable_ai/phase8_explainable_ai_report.md",
        "outputs/reports/phase9_dss/phase9_dss_implementation_report.md",
        "outputs/reports/phase10_validation/phase10_validation_report.md",
    ]
    for folder in [
        "outputs/explainability/phase8_xai/figures",
        "outputs/explainability/phase8_xai/local_explanations",
        "outputs/models/regression",
        "outputs/models/classification",
    ]:
        direct_paths.extend(rel(path) for path in sorted(project_path(folder).glob("*")) if path.is_file())

    rows = []
    for item in sorted(set(direct_paths)):
        path = project_path(item)
        category = item.split("/")[1] if item.startswith("outputs/") and len(item.split("/")) > 1 else item.split("/")[0]
        rows.append(
            {
                "Category": category,
                "Artifact": item,
                "Exists": path.exists(),
                "Type": path.suffix.lower().replace(".", "") or "folder",
                "Size_Bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
            }
        )
    return pd.DataFrame(rows)


def page_artifacts() -> None:
    st.subheader("Artifacts")
    inventory = artifact_inventory()
    metric_grid(
        [
            ("Artifacts Listed", format_number(len(inventory), 0), None),
            ("Available", format_number(int(inventory["Exists"].sum()), 0), None),
            ("Reports", format_number(int((inventory["Type"] == "md").sum()), 0), None),
            ("Figures", format_number(int(inventory["Type"].isin(["png", "jpg", "jpeg"]).sum()), 0), None),
        ]
    )
    categories = sorted(inventory["Category"].dropna().unique())
    selected = st.multiselect("Category", categories, default=categories)
    view = inventory[inventory["Category"].isin(selected)].copy()
    show_table(view, height=520)

    downloadable = view[(view["Exists"]) & (view["Type"].isin(["md", "json", "csv", "txt"]))].copy()
    if not downloadable.empty:
        choice = st.selectbox("Download Artifact", downloadable["Artifact"].tolist())
        path = project_path(choice)
        st.download_button(
            "Download Selected Artifact",
            data=path.read_bytes(),
            file_name=path.name,
            mime="text/plain",
        )


def sidebar() -> str:
    st.sidebar.title("Research Dashboard")
    st.sidebar.caption("Mango soil microbiome AI workflow")
    return st.sidebar.radio(
        "View",
        [
            "Overview",
            "Data Explorer",
            "Model Performance",
            "Explainability",
            "Validation",
            "Decision Support",
            "Artifacts",
        ],
    )


def main() -> None:
    st.set_page_config(
        page_title="Mango Research Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_style()
    section = sidebar()
    st.title("Mango Soil Microbiome Research Dashboard")

    if section == "Overview":
        page_overview()
    elif section == "Data Explorer":
        page_data_explorer()
    elif section == "Model Performance":
        page_model_performance()
    elif section == "Explainability":
        page_explainability()
    elif section == "Validation":
        page_validation()
    elif section == "Decision Support":
        page_decision_support()
    elif section == "Artifacts":
        page_artifacts()


if __name__ == "__main__":
    main()
