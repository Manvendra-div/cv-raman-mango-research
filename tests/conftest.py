"""Pytest configuration and fixtures."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_dataset():
    """Create a small synthetic dataset for testing."""
    np.random.seed(42)
    n_samples = 10
    
    data = {
        "Sample_ID": [f"S{i:04d}" for i in range(1, n_samples + 1)],
        "Orchard_ID": [f"O{i:03d}" for i in range(1, n_samples + 1)],
        "Village": ["Malihabad", "Kakori", "Rahimabad"] * 3 + ["Malihabad"],
        "Mango_Variety": ["Dasheri", "Langra", "Chausa"] * 3 + ["Dasheri"],
        "Soil_Depth": ["0-15cm"] * n_samples,
        "Sampling_Season": ["Pre-Flowering"] * n_samples,
        "Management": ["Organic", "Conventional"] * 5,
        "pH": np.random.uniform(6.0, 8.0, n_samples),
        "EC": np.random.uniform(0.2, 1.5, n_samples),
        "Organic_Carbon": np.random.uniform(0.5, 2.0, n_samples),
        "Total_Nitrogen": np.random.uniform(0.1, 0.5, n_samples),
        "Available_P": np.random.uniform(10, 50, n_samples),
        "Available_K": np.random.uniform(100, 400, n_samples),
        "Shannon_Index": np.random.uniform(2.0, 4.0, n_samples),
        "Simpson_Index": np.random.uniform(0.7, 0.95, n_samples),
        "Nitrogen_Fixers": np.random.uniform(5, 25, n_samples),
        "Phosphate_Solubilizers_PSB": np.random.uniform(5, 20, n_samples),
        "Mango_Yield": np.random.uniform(80, 200, n_samples),
        "Disease_Risk": ["Low", "Medium", "High"] * 3 + ["Low"],
        "Nutrient_Availability": ["Sufficient", "Deficient"] * 5,
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_features():
    """Create sample feature array for model input."""
    np.random.seed(42)
    return pd.DataFrame({
        "pH": [7.2, 6.8, 7.5],
        "EC": [0.8, 1.2, 0.6],
        "Organic_Carbon": [1.2, 1.5, 1.0],
        "Total_Nitrogen": [0.25, 0.30, 0.20],
        "Available_P": [25.0, 35.0, 20.0],
        "Available_K": [250.0, 300.0, 200.0],
        "Shannon_Index": [3.2, 3.5, 2.8],
        "Nitrogen_Fixers": [15.0, 18.0, 12.0],
    })


@pytest.fixture
def model_paths(project_root):
    """Return paths to trained models."""
    models_dir = project_root / "outputs" / "models"
    return {
        "regression": models_dir / "regression" / "GradientBoosting_model.joblib",
        "classification": models_dir / "classification" / "GradientBoosting_model.joblib",
    }


@pytest.fixture
def example_prediction_input():
    """Create example input for API predictions."""
    return {
        "pH": 7.2,
        "EC": 0.8,
        "Organic_Carbon": 1.2,
        "Total_Nitrogen": 0.25,
        "Available_P": 25.0,
        "Available_K": 250.0,
        "Soil_Moisture": 18.0,
        "CEC": 15.0,
        "Zn": 1.2,
        "Fe": 8.5,
        "Mn": 5.0,
        "Cu": 2.0,
        "Shannon_Index": 3.2,
        "Simpson_Index": 0.85,
        "Pielou_Evenness": 0.75,
        "OTU_Count": 450,
        "Chao1_Richness": 520,
        "Nitrogen_Fixers": 15.0,
        "Phosphate_Solubilizers_PSB": 12.0,
        "Potassium_Solubilizers": 8.0,
        "Mycorrhizae_AMF": 20.0,
        "Trichoderma": 5.0,
        "Pseudomonas_PGPR": 10.0,
        "Fusarium": 2.0,
        "Pathogen_Load_Index": 1.5,
    }
