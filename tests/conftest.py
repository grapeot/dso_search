"""
Pytest configuration and fixtures.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_dso_data():
    """
    Fixture providing sample DSO data for testing.
    """
    return pd.DataFrame({
        'name': ['M31', 'M42', 'M45'],
        'ra': [10.68458, 83.82208, 56.75000],
        'dec': [41.26917, -5.39111, 24.11667],
        'diameter': [178.0, 85.0, 110.0],
        'type': ['galaxy', 'nebula', 'cluster'],
        'catalog': ['Messier', 'Messier', 'Messier'],
        'catalog_id': ['M31', 'M42', 'M45']
    })

@pytest.fixture
def data_dir(tmp_path):
    """
    Fixture providing temporary data directory.
    """
    return tmp_path / "data"
