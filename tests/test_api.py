import requests
import json
from typing import Dict, Any

def test_healthz() -> None:
    print("\nTesting /healthz endpoint...")
    response = requests.get("http://localhost:8000/healthz")
    print(json.dumps(response.json(), indent=2))

def test_search(name: str, ra: float, dec: float, fov_width: float, fov_height: float) -> None:
    print(f"\nTesting /search endpoint with {name} coordinates...")
    params = {
        "center_ra": ra,
        "center_dec": dec,
        "fov_width": fov_width,
        "fov_height": fov_height
    }
    response = requests.get("http://localhost:8000/search", params=params)
    print(json.dumps(response.json(), indent=2))

def test_total_records() -> None:
    print("\nChecking total number of records...")
    params = {
        "center_ra": 0,
        "center_dec": 0,
        "fov_width": 360,
        "fov_height": 180
    }
    response = requests.get("http://localhost:8000/search", params=params)
    data = response.json()
    print(f"Total records: {data['total']}")
    
    # Print sample of records to verify format
    print("\nSample record format:")
    if data["objects"]:
        print(json.dumps(data["objects"][0], indent=2))

if __name__ == "__main__":
    test_healthz()
    test_search("M31 (Andromeda)", 10.6847, 41.2687, 2.0, 2.0)
    test_search("M45 (Pleiades)", 56.75, 24.1167, 2.0, 2.0)
    test_total_records()
