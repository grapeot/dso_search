"""
Pytest configuration and fixtures for DSO Search API tests.
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def sample_catalog_data(test_data_dir):
    """Create sample catalog data for testing."""
    df = pd.DataFrame({
        'name': ['M31', 'NGC 7000', 'M42'],
        'catalog': ['Messier', 'NGC', 'Messier'],
        'ra': [10.68458, 315.7, 83.82208],
        'dec': [41.26917, 44.3, -5.39111],
        'size': [178.0, 120.0, 85.0]
    })

    # Save to test directory
    data_path = Path(test_data_dir) / "processed"
    data_path.mkdir(exist_ok=True)
    df.to_csv(data_path / "test_catalog.csv", index=False)

    return df
