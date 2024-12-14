import pytest
import requests
import json
from typing import Dict, Any

def test_healthz() -> None:
    print("\nTesting /healthz endpoint...")
    response = requests.get("http://localhost:8000/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print(json.dumps(data, indent=2))

@pytest.mark.parametrize("test_params", [
    {
        "name": "M31 (Andromeda)",
        "center_ra": 10.6847,
        "center_dec": 41.2687,
        "fov_width": 2.0,
        "fov_height": 2.0
    },
    {
        "name": "M45 (Pleiades)",
        "center_ra": 56.75,
        "center_dec": 24.1167,
        "fov_width": 2.0,
        "fov_height": 2.0
    }
])
def test_search(test_params: Dict[str, Any]) -> None:
    print(f"\nTesting /search endpoint with {test_params['name']} coordinates...")
    params = {
        "center_ra": test_params["center_ra"],
        "center_dec": test_params["center_dec"],
        "fov_width": test_params["fov_width"],
        "fov_height": test_params["fov_height"]
    }
    response = requests.get("http://localhost:8000/search", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "objects" in data
    assert "total" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["objects"], list)
    print(json.dumps(data, indent=2))

def test_total_records() -> None:
    print("\nChecking total number of records...")
    params = {
        "center_ra": 0,
        "center_dec": 0,
        "fov_width": 360,
        "fov_height": 180
    }
    response = requests.get("http://localhost:8000/search", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "objects" in data
    print(f"Total records: {data['total']}")

    if data["objects"]:
        print("\nSample record format:")
        print(json.dumps(data["objects"][0], indent=2))
