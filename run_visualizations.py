#!/usr/bin/env python3
"""
Runner script for generating visualizations of the Deep Space Object catalog data.
This script loads the processed catalog data and creates various visualizations
to illustrate the composition and quality of the data.
"""
from pathlib import Path
from dso_search.catalog import process_messier, process_ngc
from dso_search.utils.visualize_data import load_data, create_visualizations

def main():
    # Ensure data directories exist
    for dir_name in ['raw', 'processed', 'intermediate', 'visualizations']:
        Path(f'data/{dir_name}').mkdir(parents=True, exist_ok=True)

    # Process catalogs
    print("Processing Messier catalog...")
    process_messier.process_messier_catalog()
    print("Processing NGC catalog...")
    process_ngc.process_ngc_catalog()

    # Generate visualizations
    print("Generating visualizations...")
    df = load_data()
    create_visualizations(df)
    print("Visualizations completed. Check data/visualizations/ directory for output.")

if __name__ == "__main__":
    main()
