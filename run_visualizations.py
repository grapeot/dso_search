#!/usr/bin/env python3
"""
Script to generate data composition visualizations.
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from dso_search.utils.visualize_data import create_visualizations

if __name__ == '__main__':
    create_visualizations()
