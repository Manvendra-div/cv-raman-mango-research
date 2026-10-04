"""Streamlit farmer + researcher dashboard. Dual audience; units shown; synthetic-data caveat banner."""
import streamlit as st, requests
st.set_page_config(page_title="Zone-Aware Mango Soil Intelligence and Yield Gap DSS", layout="wide")
st.title("Zone-Aware Mango Soil Intelligence and Yield Gap DSS")
st.warning("Research prototype trained on SYNTHETIC data — validate with field tests before action.")
API = st.sidebar.text_input("API base", "http://127.0.0.1:8000")
sec = st.sidebar.radio("Section", ["Overview","Soil Input","Prediction","Benchmark & Gap","XAI","Recommendations","Report"])
if sec == "Overview":
    st.markdown("Malihabad · Rahimabad · Kakori · Mall — Yield (kg/tree), Disease Risk, Nutrient Status, zone benchmarking, yield-gap, SHAP/LIME.")
    try: st.json(requests.get(f"{API}/health", timeout=5).json())
    except Exception as e: st.error(f"API unreachable: {e}")
elif sec == "Soil Input":
    st.subheader("Soil sample input (units shown)")
    c1, c2 = st.columns(2)
    with c1: village = st.selectbox("Village", ["Malihabad","Rahimabad","Kakori","Mall"]); variety = st.selectbox("Variety", ["Dashehari","Chausa","Safeda","Langra"]); ph = st.number_input("pH (-)", 3.5, 10.5, 7.0); oc = st.number_input("Organic Carbon (%)", 0.0, 5.0, 0.6)
    with c2: zn = st.number_input("Zn (mg/kg)", 0.0, 50.0, 0.8); k = st.number_input("Available K (kg/ha)", 0.0, 800.0, 200.0); pli = st.number_input("Pathogen Load Index (0-1)", 0.0, 1.0, 0.4)
    st.info("Required: village, variety, pH, OC, Zn, K. Optional: full microbiome panel via API /predict.")
else:
    st.subheader(sec)
    st.write("Connects to FastAPI /predict, /zone-analysis, /explain, /recommendations. See API docs.")
    st.code(f"curl {API}/metadata")
