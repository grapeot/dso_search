"""
Tests for the DSO Search API endpoints and functionality.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd

from dso_search.api.main import app
from dso_search.api.models import Coordinates, DeepSpaceObject, SearchResponse

client = TestClient(app)

@pytest.fixture
def sample_data():
    """Create sample catalog data for testing."""
    return pd.DataFrame({
        'name': ['M31', 'NGC 7000'],
        'catalog': ['Messier', 'NGC'],
        'ra': [10.68458, 315.7],
        'dec': [41.26917, 44.3],
        'size': [178.0, 120.0]
    })

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "catalog_count" in data

def test_search_valid_coordinates():
    """Test searching with valid coordinates."""
    coords = {
        "ra": 10.68458,
        "dec": 41.26917,
        "radius": 1.0
    }
    response = client.post("/search", json=coords)
    assert response.status_code == 200
    data = response.json()
    assert "objects" in data
    assert "count" in data
    assert isinstance(data["objects"], list)
    assert isinstance(data["count"], int)

def test_search_invalid_coordinates():
    """Test searching with invalid coordinates."""
    # Test invalid RA
    coords = {
        "ra": 400,  # Invalid RA (>360)
        "dec": 41.26917,
        "radius": 1.0
    }
    response = client.post("/search", json=coords)
    assert response.status_code == 422

    # Test invalid Dec
    coords = {
        "ra": 10.68458,
        "dec": 100,  # Invalid Dec (>90)
        "radius": 1.0
    }
    response = client.post("/search", json=coords)
    assert response.status_code == 422

    # Test invalid radius
    coords = {
        "ra": 10.68458,
        "dec": 41.26917,
        "radius": -1  # Invalid radius (<0)
    }
    response = client.post("/search", json=coords)
    assert response.status_code == 422

def test_list_catalogs():
    """Test listing available catalogs."""
    response = client.get("/catalogs")
    assert response.status_code == 200
    data = response.json()
    assert "catalogs" in data
    assert "total_objects" in data
    assert isinstance(data["catalogs"], dict)
    assert isinstance(data["total_objects"], int)

def test_search_response_format():
    """Test the format of search response objects."""
    coords = {
        "ra": 10.68458,
        "dec": 41.26917,
        "radius": 1.0
    }
    response = client.post("/search", json=coords)
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "objects" in data
    assert "count" in data

    # If any objects returned, verify their structure
    if data["objects"]:
        obj = data["objects"][0]
        assert "name" in obj
        assert "catalog" in obj
        assert "ra" in obj
        assert "dec" in obj
        assert "size" in obj

        # Verify data types
        assert isinstance(obj["name"], str)
        assert isinstance(obj["catalog"], str)
        assert isinstance(obj["ra"], (int, float))
        assert isinstance(obj["dec"], (int, float))
        assert obj["size"] is None or isinstance(obj["size"], (int, float))
