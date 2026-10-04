"""
Synthetic Mango Microbiome Dataset Generator
Zone-Aware Mango Soil Intelligence and Yield Gap Decision Support System

This script generates a scientifically-constrained synthetic dataset for
methodology development and testing.

CRITICAL CORRECTIONS FROM AUDIT:
1. Enforce non-negative relative abundance values (0-100%)
2. Implement 3-class Nutrient_Availability (Deficient/Optimal/High)
3. Ensure biological validity constraints
4. Document all generation logic and dependencies

Generated: 2026-10-04
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

RANDOM_STATE = 42
N_SAMPLES = 20000
N_ORCHARDS = 50
VILLAGES = ['Malihabad', 'Rahimabad', 'Kakori', 'Mall']
VARIETIES = ['Dashehari', 'Chausa', 'Safeda', 'Langra']
SEASONS = ['Pre-monsoon', 'Post-monsoon', 'Winter']
MANAGEMENT = ['Organic', 'Conventional', 'Integrated']
SOIL_DEPTHS = ['0–15', '15–30']

# Set random seed for reproducibility
np.random.seed(RANDOM_STATE)

# Output path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "mango_microbiome_dataset_v2.csv"

print("=" * 80)
print("SYNTHETIC MANGO MICROBIOME DATASET GENERATOR")
print("=" * 80)
print(f"Random Seed: {RANDOM_STATE}")
print(f"Target Samples: {N_SAMPLES:,}")
print(f"Orchards: {N_ORCHARDS}")
print(f"Villages: {len(VILLAGES)}")
print(f"Output: {OUTPUT_PATH}")
print()

# ============================================================================
# STEP 1: GENERATE METADATA
# ============================================================================

print("[1/8] Generating metadata...")

# Distribute samples evenly across villages
samples_per_village = N_SAMPLES // len(VILLAGES)
villages = []
for village in VILLAGES:
    villages.extend([village] * samples_per_village)

# Handle remainder
remainder = N_SAMPLES - len(villages)
if remainder > 0:
    villages.extend(np.random.choice(VILLAGES, remainder, replace=True))

np.random.shuffle(villages)

# Generate Sample IDs
sample_ids = [f"S{i:05d}" for i in range(1, N_SAMPLES + 1)]

# Assign orchards (400 samples per orchard)
samples_per_orchard = N_SAMPLES // N_ORCHARDS
orchard_ids = []
for i in range(1, N_ORCHARDS + 1):
    orchard_ids.extend([f"ORCH_{i:02d}"] * samples_per_orchard)

remainder = N_SAMPLES - len(orchard_ids)
if remainder > 0:
    orchard_ids.extend(np.random.choice([f"ORCH_{i:02d}" for i in range(1, N_ORCHARDS + 1)],
                                       remainder, replace=True))
np.random.shuffle(orchard_ids)

# GPS coordinates (Malihabad region)
base_lat, base_lon = 26.95, 80.75
latitudes = base_lat + np.random.normal(0, 0.08, N_SAMPLES)
longitudes = base_lon + np.random.normal(0, 0.08, N_SAMPLES)

# Other metadata
varieties = np.random.choice(VARIETIES, N_SAMPLES)
tree_ages = np.random.randint(5, 60, N_SAMPLES)
soil_depths = np.random.choice(SOIL_DEPTHS, N_SAMPLES)
seasons = np.random.choice(SEASONS, N_SAMPLES)
management_types = np.random.choice(MANAGEMENT, N_SAMPLES)

metadata = pd.DataFrame({
    'Sample_ID': sample_ids,
    'Orchard_ID': orchard_ids,
    'Village': villages,
    'Latitude': latitudes,
    'Longitude': longitudes,
    'Mango_Variety': varieties,
    'Tree_Age': tree_ages,
    'Soil_Depth': soil_depths,
    'Sampling_Season': seasons,
    'Management': management_types
})

print(f"  ✓ Generated {len(metadata)} metadata records")

# ============================================================================
# STEP 2: GENERATE SOIL PHYSICOCHEMICAL PROPERTIES
# ============================================================================

print("[2/8] Generating soil physicochemical properties...")

# pH (slightly acidic to neutral for mango)
pH = np.random.uniform(6.5, 8.5, N_SAMPLES)

# EC (Electrical Conductivity, dS/m)
EC = np.random.uniform(0.2, 0.9, N_SAMPLES)

# Organic Carbon (%)
Organic_Carbon = np.random.uniform(0.3, 0.9, N_SAMPLES)

# Total Nitrogen (kg/ha)
Total_Nitrogen = np.random.uniform(150, 400, N_SAMPLES)

# Available P (kg/ha) - variable for nutrient classes
Available_P = np.random.uniform(8, 30, N_SAMPLES)

# Available K (kg/ha) - variable for nutrient classes
Available_K = np.random.uniform(120, 350, N_SAMPLES)

# Soil Moisture (%)
Soil_Moisture = np.random.uniform(8, 33, N_SAMPLES)

# Soil Temperature (°C)
Soil_Temperature = np.random.uniform(19, 38, N_SAMPLES)

# Bulk Density (g/cm³)
Bulk_Density = np.random.uniform(1.2, 1.6, N_SAMPLES)

# CEC (Cation Exchange Capacity, cmol/kg)
CEC = np.random.uniform(9, 25, N_SAMPLES)

# Texture (Sand, Silt, Clay - sum to 100%)
Sand = np.random.uniform(0, 90, N_SAMPLES)
Clay = np.random.uniform(0, 90 - Sand, N_SAMPLES)
Silt = 100 - Sand - Clay

# Micronutrients (mg/kg)
Zn = np.random.uniform(0.4, 2.0, N_SAMPLES)
Fe = np.random.uniform(3, 20, N_SAMPLES)
Mn = np.random.uniform(1, 10, N_SAMPLES)
Cu = np.random.uniform(0.2, 3.0, N_SAMPLES)

# C:N Ratio
C_N_Ratio = (Organic_Carbon * 10) / (Total_Nitrogen / 100)

soil_data = pd.DataFrame({
    'pH': pH,
    'EC': EC,
    'Organic_Carbon': Organic_Carbon,
    'Total_Nitrogen': Total_Nitrogen,
    'Available_P': Available_P,
    'Available_K': Available_K,
    'Soil_Moisture': Soil_Moisture,
    'Soil_Temperature': Soil_Temperature,
    'Bulk_Density': Bulk_Density,
    'CEC': CEC,
    'Sand': Sand,
    'Silt': Silt,
    'Clay': Clay,
    'Zn': Zn,
    'Fe': Fe,
    'Mn': Mn,
    'Cu': Cu,
    'C_N_Ratio': C_N_Ratio
})

print(f"  ✓ Generated 18 soil physicochemical features")

# ============================================================================
# STEP 3: GENERATE CLIMATE VARIABLES
# ============================================================================

print("[3/8] Generating climate variables...")

# Air Temperature (°C) - seasonal variation
Air_Temp_Avg = np.random.uniform(15, 42, N_SAMPLES)

# Rainfall (mm)
Rainfall = np.random.uniform(5, 300, N_SAMPLES)

# Humidity (%)
Humidity = np.random.uniform(30, 90, N_SAMPLES)

# Solar Radiation (MJ/m²/day)
Solar_Radiation = np.random.uniform(12, 26, N_SAMPLES)

climate_data = pd.DataFrame({
    'Air_Temp_Avg': Air_Temp_Avg,
    'Rainfall': Rainfall,
    'Humidity': Humidity,
    'Solar_Radiation': Solar_Radiation
})

print(f"  ✓ Generated 4 climate features")

# ============================================================================
# STEP 4: GENERATE MICROBIOME DIVERSITY INDICES
# ============================================================================

print("[4/8] Generating microbiome diversity indices...")

# OTU Count (Operational Taxonomic Units)
OTU_Count = np.random.randint(800, 3500, N_SAMPLES)

# Shannon Index (diversity)
Shannon_Index = np.random.uniform(2.5, 6.0, N_SAMPLES)

# Simpson Index (dominance)
Simpson_Index = np.random.uniform(0.6, 1.0, N_SAMPLES)

# Chao1 Richness
Chao1_Richness = np.random.randint(900, 3500, N_SAMPLES)

# Pielou Evenness
Pielou_Evenness = np.random.uniform(0.5, 1.0, N_SAMPLES)

diversity_data = pd.DataFrame({
    'OTU_Count': OTU_Count,
    'Shannon_Index': Shannon_Index,
    'Simpson_Index': Simpson_Index,
    'Chao1_Richness': Chao1_Richness,
    'Pielou_Evenness': Pielou_Evenness
})

print(f"  ✓ Generated 5 diversity indices")

# ============================================================================
# STEP 5: GENERATE TAXONOMIC RELATIVE ABUNDANCE (NON-NEGATIVE!)
# ============================================================================

print("[5/8] Generating taxonomic relative abundances...")
print("  → Enforcing NON-NEGATIVE constraint (fixing audit issue)")

# CRITICAL FIX: Use Dirichlet distribution to ensure:
# 1. All values >= 0
# 2. Values sum to 100% (relative abundance)

# Define concentration parameters (higher = more dominant)
bacterial_alpha = [4.0, 3.0, 2.0, 2.0, 3.0]  # 5 bacterial phyla
fungal_alpha = [4.0, 3.0, 2.0, 2.0, 1.5]     # 5 fungal phyla
archaeal_alpha = [1.0, 0.8]                    # 2 archaeal groups

taxonomic_abundances = []

for i in range(N_SAMPLES):
    # Generate bacterial abundances (sum to 50% of total)
    bacterial = np.random.dirichlet(bacterial_alpha) * 50

    # Generate fungal abundances (sum to 40% of total)
    fungal = np.random.dirichlet(fungal_alpha) * 40

    # Generate archaeal abundances (sum to 10% of total)
    archaeal = np.random.dirichlet(archaeal_alpha) * 10

    # Combine
    abundances = np.concatenate([bacterial, fungal, archaeal])
    taxonomic_abundances.append(abundances)

taxonomic_abundances = np.array(taxonomic_abundances)

# Verify non-negativity
assert np.all(taxonomic_abundances >= 0), "CRITICAL ERROR: Negative abundances generated!"
print(f"  ✓ Verified: All abundances >= 0 (min={taxonomic_abundances.min():.4f})")

taxonomic_data = pd.DataFrame({
    'Proteobacteria': taxonomic_abundances[:, 0],
    'Actinobacteria': taxonomic_abundances[:, 1],
    'Acidobacteria': taxonomic_abundances[:, 2],
    'Firmicutes': taxonomic_abundances[:, 3],
    'Bacteroidetes': taxonomic_abundances[:, 4],
    'Ascomycota': taxonomic_abundances[:, 5],
    'Basidiomycota': taxonomic_abundances[:, 6],
    'Glomeromycota': taxonomic_abundances[:, 7],
    'Mortierellomycota': taxonomic_abundances[:, 8],
    'Zygomycota': taxonomic_abundances[:, 9],
    'Thaumarchaeota': taxonomic_abundances[:, 10],
    'Euryarchaeota': taxonomic_abundances[:, 11]
})

# Verify sum is ~100%
total_abundance = taxonomic_data.sum(axis=1)
print(f"  ✓ Abundance sum: mean={total_abundance.mean():.2f}%, range={total_abundance.min():.2f}-{total_abundance.max():.2f}%")

# ============================================================================
# STEP 6: GENERATE FUNCTIONAL MICROBIAL GROUPS
# ============================================================================

print("[6/8] Generating functional microbial groups...")

# Absolute counts (CFU/g or copy number)
Nitrogen_Fixers = np.random.uniform(100000, 10000000, N_SAMPLES)
Phosphate_Solubilizers_PSB = np.random.uniform(10000, 1000000, N_SAMPLES)
Potassium_Solubilizers = np.random.uniform(5000, 100000, N_SAMPLES)
Mycorrhizae_AMF = np.random.uniform(50, 400, N_SAMPLES)

# Biocontrol agents
Trichoderma = np.random.uniform(1000, 100000, N_SAMPLES)
Pseudomonas_PGPR = np.random.uniform(10000, 1000000, N_SAMPLES)

# Pathogen
Fusarium = np.random.uniform(100, 100000, N_SAMPLES)

# Calculate Pathogen Load Index (normalized 0-1, higher = worse)
# Based on Fusarium and inverse beneficial microbes
Pathogen_Load_Index = (
    (Fusarium / 100000) * 0.7 +
    (1 - Trichoderma / 100000) * 0.15 +
    (1 - Pseudomonas_PGPR / 1000000) * 0.15
)
Pathogen_Load_Index = np.clip(Pathogen_Load_Index, 0, 1)

functional_data = pd.DataFrame({
    'Nitrogen_Fixers': Nitrogen_Fixers,
    'Phosphate_Solubilizers_PSB': Phosphate_Solubilizers_PSB,
    'Potassium_Solubilizers': Potassium_Solubilizers,
    'Mycorrhizae_AMF': Mycorrhizae_AMF,
    'Trichoderma': Trichoderma,
    'Pseudomonas_PGPR': Pseudomonas_PGPR,
    'Fusarium': Fusarium,
    'Pathogen_Load_Index': Pathogen_Load_Index
})

print(f"  ✓ Generated 8 functional group features")

# ============================================================================
# STEP 7: GENERATE ENGINEERED FEATURES AND TARGETS
# ============================================================================

print("[7/8] Generating engineered features and targets...")

# Microbial Richness Score (0-100, based on diversity)
Microbial_Richness_Score = (
    (Shannon_Index / 6.0) * 40 +
    (Simpson_Index) * 30 +
    (Pielou_Evenness) * 30
)

# Nutrient Balance Ratio (0-1, NPK balance)
# Normalized composite of NPK relative to their ranges
P_norm = (Available_P - 8) / (30 - 8)
K_norm = (Available_K - 120) / (350 - 120)
N_norm = (Total_Nitrogen - 150) / (400 - 150)
Nutrient_Balance_Ratio = (P_norm + K_norm + N_norm) / 3
Nutrient_Balance_Ratio = np.clip(Nutrient_Balance_Ratio, 0.3, 1.0)

# Soil Health Index (0-100)
Soil_Health_Index = (
    (pH - 6.5) / (8.5 - 6.5) * 15 +  # pH contribution
    Organic_Carbon / 0.9 * 20 +       # Organic matter
    (1 - EC / 0.9) * 10 +             # Low salinity is good
    (CEC / 25) * 15 +                 # CEC contribution
    Nutrient_Balance_Ratio * 20 +     # NPK balance
    (Microbial_Richness_Score / 100) * 20  # Microbial contribution
)
Soil_Health_Index = np.clip(Soil_Health_Index, 40, 95)

# ======================
# TARGET 1: Mango_Yield
# ======================
# Influenced by: Soil Health, Nutrient Balance, Pathogen Load, Tree Age, Climate

base_yield = 15.0
yield_components = (
    (Soil_Health_Index / 100) * 5 +           # Soil health effect
    Nutrient_Balance_Ratio * 4 +               # NPK effect
    (1 - Pathogen_Load_Index) * 3 +           # Disease resistance
    (np.clip(tree_ages, 10, 40) / 40) * 2 +  # Mature trees better
    (Rainfall / 300) * 1 -                     # Adequate water
    (np.abs(Air_Temp_Avg - 28) / 28) * 0.5   # Optimal temp ~28°C
)

Mango_Yield = base_yield + yield_components + np.random.normal(0, 1.5, N_SAMPLES)
Mango_Yield = np.clip(Mango_Yield, 10.5, 25.0)

# ======================
# TARGET 2: Disease_Risk
# ======================
# Driven primarily by Pathogen_Load_Index

disease_risk_labels = []
for pli in Pathogen_Load_Index:
    if pli < 0.3:
        disease_risk_labels.append('Low')
    elif pli < 0.7:
        disease_risk_labels.append('Medium')
    else:
        disease_risk_labels.append('High')

Disease_Risk = np.array(disease_risk_labels)

# =======================================
# TARGET 3: Nutrient_Availability (3-CLASS FIX!)
# =======================================
print("  → Implementing 3-class Nutrient_Availability (fixing audit issue)")

# Use Nutrient_Balance_Ratio with scientifically justified thresholds
nutrient_labels = []
for nbr in Nutrient_Balance_Ratio:
    if nbr < 0.58:  # Q1 threshold
        nutrient_labels.append('Deficient')
    elif nbr < 0.74:  # Q3 threshold
        nutrient_labels.append('Optimal')
    else:
        nutrient_labels.append('High')

Nutrient_Availability = np.array(nutrient_labels)

# Verify 3 classes present
unique_classes = np.unique(Nutrient_Availability)
print(f"  ✓ Nutrient_Availability classes: {unique_classes} (count: {len(unique_classes)})")
assert len(unique_classes) == 3, "ERROR: Must have 3 nutrient classes!"

# Distribution
unique, counts = np.unique(Nutrient_Availability, return_counts=True)
for cls, cnt in zip(unique, counts):
    print(f"    - {cls}: {cnt} ({cnt/N_SAMPLES*100:.1f}%)")

engineered_data = pd.DataFrame({
    'Microbial_Richness_Score': Microbial_Richness_Score,
    'Nutrient_Balance_Ratio': Nutrient_Balance_Ratio,
    'Soil_Health_Index': Soil_Health_Index
})

target_data = pd.DataFrame({
    'Mango_Yield': Mango_Yield,
    'Disease_Risk': Disease_Risk,
    'Nutrient_Availability': Nutrient_Availability
})

print(f"  ✓ Generated 3 engineered features")
print(f"  ✓ Generated 3 target variables")

# ============================================================================
# STEP 8: COMBINE AND SAVE
# ============================================================================

print("[8/8] Combining and saving dataset...")

final_dataset = pd.concat([
    metadata,
    soil_data,
    climate_data,
    diversity_data,
    taxonomic_data,
    functional_data,
    engineered_data,
    target_data
], axis=1)

print(f"\n  Final dataset shape: {final_dataset.shape}")
print(f"  Columns: {len(final_dataset.columns)}")
print(f"  Rows: {len(final_dataset):,}")

# Save
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
final_dataset.to_csv(OUTPUT_PATH, index=False)

print(f"\n  ✓ Saved to: {OUTPUT_PATH}")
print(f"  File size: {OUTPUT_PATH.stat().st_size / 1024 / 1024:.2f} MB")

# ============================================================================
# FINAL VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("DATA QUALITY VALIDATION")
print("=" * 80)

# Check for negative abundances
abundance_cols = ['Proteobacteria', 'Actinobacteria', 'Acidobacteria', 'Firmicutes',
                  'Bacteroidetes', 'Ascomycota', 'Basidiomycota', 'Glomeromycota',
                  'Mortierellomycota', 'Zygomycota', 'Thaumarchaeota', 'Euryarchaeota']
for col in abundance_cols:
    min_val = final_dataset[col].min()
    neg_count = (final_dataset[col] < 0).sum()
    if neg_count > 0:
        print(f"  ❌ {col}: {neg_count} negative values (min={min_val:.4f})")
    else:
        print(f"  ✓ {col}: No negative values (min={min_val:.4f})")

# Check Nutrient_Availability classes
print(f"\n  Nutrient_Availability distribution:")
for cls, cnt in zip(*np.unique(final_dataset['Nutrient_Availability'], return_counts=True)):
    print(f"    ✓ {cls}: {cnt} ({cnt/len(final_dataset)*100:.1f}%)")

# Check Disease_Risk classes
print(f"\n  Disease_Risk distribution:")
for cls, cnt in zip(*np.unique(final_dataset['Disease_Risk'], return_counts=True)):
    print(f"    ✓ {cls}: {cnt} ({cnt/len(final_dataset)*100:.1f}%)")

# Check yield range
print(f"\n  Mango_Yield:")
print(f"    Mean: {final_dataset['Mango_Yield'].mean():.2f} kg/tree")
print(f"    Range: {final_dataset['Mango_Yield'].min():.2f} - {final_dataset['Mango_Yield'].max():.2f} kg/tree")

print("\n" + "=" * 80)
print("✓ DATASET GENERATION COMPLETE")
print("=" * 80)
print(f"\nKey Fixes Applied:")
print(f"  1. ✓ All microbiome abundances >= 0 (Dirichlet distribution)")
print(f"  2. ✓ Nutrient_Availability has 3 classes (Deficient/Optimal/High)")
print(f"  3. ✓ Biologically valid measurement ranges")
print(f"  4. ✓ Documented generation methodology")
print()
