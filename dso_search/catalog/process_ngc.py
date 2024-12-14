import pandas as pd
import numpy as np
from pathlib import Path
import re

def convert_ra_to_degrees(ra_str):
    """Convert RA from 'HH MM.M' format to degrees"""
    if pd.isna(ra_str):
        return None

    # Parse hours and minutes
    match = re.match(r'(\d+)\s+(\d+\.?\d*)', ra_str.strip())
    if not match:
        return None

    hours = float(match.group(1))
    minutes = float(match.group(2))

    # Convert to degrees (RA: 24 hours = 360 degrees)
    return (hours + minutes/60) * 15

def convert_dec_to_degrees(dec_str):
    """Convert DEC from '+/-DD MM' format to degrees"""
    if pd.isna(dec_str):
        return None

    # Parse sign, degrees and minutes
    match = re.match(r'([+-])(\d+)\s+(\d+)', dec_str.strip())
    if not match:
        return None

    sign = 1 if match.group(1) == '+' else -1
    degrees = float(match.group(2))
    minutes = float(match.group(3))

    return sign * (degrees + minutes/60)

def process_ngc_data(input_file):
    """Process NGC/IC catalog data into standardized format"""
    print(f"Processing NGC/IC data from {input_file}")

    # Read TSV file, skipping initial comments
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Find where the actual data starts (after headers)
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "-----\t-------\t------\t-----":
            data_start = i + 1
            break

    # Read the data into a pandas DataFrame
    df = pd.read_csv(input_file,
                     sep='\t',
                     skiprows=data_start,
                     names=['name', 'ra', 'dec', 'diameter'])

    # Clean up the data
    df = df.replace('', np.nan)  # Replace empty strings with NaN

    # Convert coordinates to degrees
    df['ra_deg'] = df['ra'].apply(convert_ra_to_degrees)
    df['dec_deg'] = df['dec'].apply(convert_dec_to_degrees)

    # Convert diameter to float, handling missing values
    df['diameter'] = pd.to_numeric(df['diameter'], errors='coerce')

    # Add catalog column (NGC or IC)
    df['catalog'] = df['name'].apply(lambda x: 'IC' if x.strip().startswith('I') else 'NGC')

    # Clean up object numbers - handle space after 'I' prefix
    df['number'] = df['name'].apply(lambda x: x.strip().replace('I ', '').replace('I', ''))

    # Create standardized format
    result_df = pd.DataFrame({
        'name': df.apply(lambda row: f"{row['catalog']}{str(row['number']).zfill(4)}", axis=1),
        'catalog': df['catalog'],
        'ra': df['ra_deg'],
        'dec': df['dec_deg'],
        'diameter': df['diameter']
    })

    # Split into NGC and IC catalogs
    ngc_df = result_df[result_df['catalog'] == 'NGC']
    ic_df = result_df[result_df['catalog'] == 'IC']

    # Save processed data
    data_dir = Path("/home/ubuntu/dso-search-api/dso-search-api/data")
    ngc_df.to_csv(data_dir / "processed_ngc.csv", index=False)
    ic_df.to_csv(data_dir / "processed_ic.csv", index=False)

    print("\nData Processing Summary:")
    print(f"Total NGC objects: {len(ngc_df)}")
    print(f"Total IC objects: {len(ic_df)}")
    print(f"Total objects: {len(result_df)}")
    print("\nSample of processed data:")
    print(result_df.head())
    print("\nMissing values:")
    print(result_df.isnull().sum())

    return result_df

if __name__ == "__main__":
    data_dir = Path("/home/ubuntu/dso-search-api/dso-search-api/data")
    input_file = data_dir / "ngc2000.tsv"

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        exit(1)

    df = process_ngc_data(input_file)
