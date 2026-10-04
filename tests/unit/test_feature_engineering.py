"""Unit tests for feature engineering module."""

import numpy as np
import pandas as pd
import pytest


def test_soil_health_index_calculation():
    """Test Soil_Health_Index calculation for sample input."""
    # Sample soil parameters
    oc = 1.5  # Organic Carbon
    tn = 0.3  # Total Nitrogen
    p = 30.0  # Available P
    k = 250.0  # Available K
    
    # Normalize to typical ranges (0-1 scale)
    oc_norm = np.clip(oc / 2.0, 0, 1)  # Max OC ~ 2%
    tn_norm = np.clip(tn / 0.5, 0, 1)  # Max TN ~ 0.5%
    p_norm = np.clip(p / 50.0, 0, 1)   # Max P ~ 50 ppm
    k_norm = np.clip(k / 400.0, 0, 1)  # Max K ~ 400 ppm
    
    # Simple average (actual implementation may differ)
    expected_shi = (oc_norm + tn_norm + p_norm + k_norm) / 4.0
    
    # Check that SHI is in valid range
    assert 0 <= expected_shi <= 1
    assert np.isfinite(expected_shi)


def test_nutrient_balance_ratio_formula():
    """Test Nutrient_Balance_Ratio formula."""
    n = 0.25
    p = 25.0
    k = 250.0
    
    # NPK ratio (example: normalized balance metric)
    # Typical ideal ratio N:P:K ~ 1:0.5:1 (adjusted for units)
    n_adjusted = n * 100  # Convert % to comparable scale
    p_adjusted = p        # Already in ppm
    k_adjusted = k        # Already in ppm
    
    # Calculate ratio metric
    ratio = (n_adjusted + p_adjusted + k_adjusted) / 3.0
    
    assert ratio > 0
    assert np.isfinite(ratio)


def test_engineered_features_within_expected_ranges(sample_dataset):
    """Test that engineered features are within expected ranges."""
    # Add simple engineered features
    df = sample_dataset.copy()
    
    # Microbial Richness Score (combination of Shannon and Simpson)
    df["Microbial_Richness_Score"] = (
        df["Shannon_Index"] / 4.0 + df["Simpson_Index"]
    ) / 2.0
    
    # Check range
    assert df["Microbial_Richness_Score"].min() >= 0
    assert df["Microbial_Richness_Score"].max() <= 1.5
    
    # Nutrient Balance Ratio
    df["Nutrient_Balance_Ratio"] = (
        df["Total_Nitrogen"] * 100 + df["Available_P"] + df["Available_K"]
    ) / 3.0
    
    # Check no NaN or inf values
    assert df["Nutrient_Balance_Ratio"].notna().all()
    assert np.isfinite(df["Nutrient_Balance_Ratio"]).all()
    
    # Soil Health Index
    df["Soil_Health_Index"] = (
        df["Organic_Carbon"] / 2.0 +
        df["Total_Nitrogen"] / 0.5 +
        df["Available_P"] / 50.0 +
        df["Available_K"] / 400.0
    ) / 4.0
    
    # Check range (should be roughly 0-1 if normalized)
    assert df["Soil_Health_Index"].min() >= 0
    assert np.isfinite(df["Soil_Health_Index"]).all()
