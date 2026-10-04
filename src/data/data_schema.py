"""Canonical data schema — 63-column raw dataset. Single source of truth."""
from __future__ import annotations
NUMERIC_RANGES = {
    "pH": (3.5, 10.5), "EC": (0.0, 5.0), "Organic_Carbon": (0.0, 5.0),
    "Total_Nitrogen": (0, 1000), "Available_P": (0, 150), "Available_K": (0, 800),
    "Soil_Moisture": (0, 100), "Soil_Temperature": (-5, 60), "Bulk_Density": (0.8, 2.2),
    "CEC": (0, 60), "Sand": (0, 100), "Silt": (0, 100), "Clay": (0, 100),
    "Zn": (0, 50), "Fe": (0, 200), "Mn": (0, 100), "Cu": (0, 50), "C_N_Ratio": (1, 40),
    "Air_Temp_Avg": (-10, 55), "Rainfall": (0, 2000), "Humidity": (0, 100),
    "Solar_Radiation": (0, 40), "OTU_Count": (0, 20000), "Shannon_Index": (0, 8),
    "Simpson_Index": (0, 1), "Chao1_Richness": (0, 20000), "Pielou_Evenness": (0, 1),
    "Microbial_Richness_Score": (0, 100), "Nutrient_Balance_Ratio": (0, 2),
    "Soil_Health_Index": (0, 100), "Pathogen_Load_Index": (0, 1),
    "Mango_Yield": (0, 200),
}
TAXA_COLS = ["Proteobacteria","Actinobacteria","Acidobacteria","Firmicutes","Bacteroidetes",
    "Ascomycota","Basidiomycota","Glomeromycota","Mortierellomycota","Zygomycota",
    "Thaumarchaeota","Euryarchaeota"]
for c in TAXA_COLS: NUMERIC_RANGES[c] = (0, 100)
CATEGORICAL = {
    "Village": ["Malihabad","Rahimabad","Kakori","Mall"],
    "Mango_Variety": ["Dashehari","Chausa","Safeda","Langra"],
    "Soil_Depth": ["0-15","0–15","15-30","15–30"],
    "Sampling_Season": ["Pre-monsoon","Post-monsoon","Winter"],
    "Management": ["Organic","Conventional","Integrated"],
    "Disease_Risk": ["Low","Medium","High"],
    "Nutrient_Availability": ["Deficient","Optimal","High"],
}
TARGETS = ["Mango_Yield","Disease_Risk","Nutrient_Availability"]
ID_COLS = ["Sample_ID","Orchard_ID","Latitude","Longitude","Tree_Age"]
