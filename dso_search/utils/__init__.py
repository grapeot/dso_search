"""
Utility functions for the DSO Search API.
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path

def load_catalog_status() -> Dict[str, Any]:
    """
    Load catalog processing status from JSON file.

    Returns:
        Dict containing catalog processing status
    """
    status_file = Path(__file__).parent.parent / "data" / "catalog_status.json"
    if not status_file.exists():
        return {}

    with open(status_file) as f:
        return json.load(f)

def update_catalog_status(catalog: str, status: Dict[str, Any]) -> None:
    """
    Update processing status for a specific catalog.

    Args:
        catalog: Catalog identifier
        status: Status information to update
    """
    status_file = Path(__file__).parent.parent / "data" / "catalog_status.json"
    current_status = load_catalog_status()

    current_status[catalog] = status

    with open(status_file, 'w') as f:
        json.dump(current_status, f, indent=2)

def get_data_dir() -> Path:
    """
    Get path to data directory.

    Returns:
        Path to data directory
    """
    return Path(__file__).parent.parent / "data"
