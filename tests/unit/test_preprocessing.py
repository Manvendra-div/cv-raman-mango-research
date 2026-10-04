"""Unit tests for preprocessing module."""

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split


def test_standard_scaler_transforms_correctly(sample_features):
    """Test that StandardScaler transforms data correctly."""
    scaler = StandardScaler()
    scaled = scaler.fit_transform(sample_features)
    
    # Check shape is preserved
    assert scaled.shape == sample_features.shape
    
    # Check mean is approximately 0 and std is approximately 1
    assert np.abs(scaled.mean(axis=0)).max() < 1e-10
    assert np.abs(scaled.std(axis=0) - 1.0).max() < 1e-10


def test_train_test_split_produces_expected_shapes(sample_dataset):
    """Test that train/test split produces expected shapes."""
    X = sample_dataset.drop(columns=["Mango_Yield", "Disease_Risk", "Nutrient_Availability"])
    y = sample_dataset["Mango_Yield"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Check split ratios
    assert len(X_train) == 7
    assert len(X_test) == 3
    assert len(y_train) == 7
    assert len(y_test) == 3
    
    # Check no data leakage
    train_indices = set(X_train.index)
    test_indices = set(X_test.index)
    assert len(train_indices.intersection(test_indices)) == 0


def test_onehot_encoder_handles_unknown_categories():
    """Test that OneHotEncoder handles unknown categories properly."""
    # Training data
    train_df = pd.DataFrame({"Village": ["Malihabad", "Kakori", "Malihabad"]})
    
    # Test data with unknown category
    test_df = pd.DataFrame({"Village": ["Malihabad", "Unknown_Village"]})
    
    # Create encoder with handle_unknown='ignore'
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoder.fit(train_df)
    
    # Transform test data
    encoded = encoder.transform(test_df)
    
    # Check that unknown category results in all zeros
    assert encoded.shape[0] == 2
    assert encoded[1].sum() == 0  # Unknown village should be all zeros
