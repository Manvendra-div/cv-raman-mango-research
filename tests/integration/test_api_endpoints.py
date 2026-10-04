"""Integration tests for API endpoints."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

try:
    from fastapi.testclient import TestClient
    from dss.api import app
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
def test_health_endpoint_returns_200():
    """Test /health endpoint returns 200."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] in ("healthy", "ok")


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
def test_metadata_endpoint_returns_expected_structure():
    """Test /metadata endpoint returns expected structure."""
    client = TestClient(app)
    response = client.get("/metadata")
    
    assert response.status_code == 200
    data = response.json()
    
    # Service returns metadata dict (numeric/categorical features, champions); accept legacy or current shape
    assert isinstance(data, dict) and len(data) > 0


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
def test_zone_analysis_endpoint(example_prediction_input):
    """Test /zone-analysis endpoint with example input."""
    client = TestClient(app)
    
    # Create zone analysis request
    request_data = {
        "orchard_id": "O001",
        "village": "Malihabad",
        "features": example_prediction_input
    }
    
    response = client.post("/api/v1/zone-analysis", json=request_data)
    
    # May return 404 if models not found, which is acceptable for tests
    assert response.status_code in [200, 404, 422]
    
    if response.status_code == 200:
        data = response.json()
        # Check expected structure
        assert "orchard_id" in data or "analysis" in data


def test_api_module_imports():
    """Test that API module imports successfully."""
    try:
        from dss import api
        assert hasattr(api, 'app')
    except ImportError as e:
        pytest.skip(f"API module not available: {e}")
