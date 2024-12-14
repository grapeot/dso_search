import pandas as pd
import numpy as np
from pathlib import Path

def process_messier_data(input_file, output_file):
    """Process Messier catalog data into standardized format"""
    print(f"Processing Messier data from {input_file}")

    # Known Messier object count (M1 through M110)
    TOTAL_MESSIER = 110

    # Download Messier object diameters from another source
    print("Fetching Messier object diameters...")
    # Using a different VizieR catalog for Messier object diameters
    diameter_url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=VII/118/mwsc&-out.max=unlimited&-out.form=TSV&-out.meta=&-out=Name&-out=r2'

    try:
        import requests
        response = requests.get(diameter_url)
        diameter_data = {}
        lines = response.text.split('\n')
        data_start = 0
        for i, line in enumerate(lines):
            if line.strip() and all(c in '-' for c in line.strip()):
                data_start = i + 1
                break

        for line in lines[data_start:]:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    messier_num = parts[0].strip()
                    diam = parts[1].strip()
                    if messier_num.isdigit():
                        diameter_data[int(messier_num)] = float(diam) if diam else None
    except:
        print("Warning: Could not fetch diameter data")
        diameter_data = {}

    # Read TSV file, skipping initial comments
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Find where the actual data starts (after headers)
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() and all(c in '-' for c in line.strip()):
            data_start = i + 1
            break

    # Process data lines manually due to inconsistent format
    data = []
    messier_count = 0
    for line in lines[data_start:]:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split('\t')
            if len(parts) >= 2 and messier_count < TOTAL_MESSIER:  # Limit to known Messier objects
                ra, dec = parts[:2]
                messier_count += 1
                data.append({
                    'RA': ra.strip(),
                    'DEC': dec.strip(),
                    'Messier': messier_count
                })

    df = pd.DataFrame(data)

    # Clean up the data
    df = df.replace('', np.nan)  # Replace empty strings with NaN
    df = df.dropna(subset=['RA', 'DEC'])  # Remove rows with missing essential data

    # Convert coordinates from HH MM.M format to degrees
    def convert_ra(ra_str):
        try:
            if pd.isna(ra_str):
                return None
            parts = ra_str.split()
            if len(parts) != 2:
                return None
            hours = float(parts[0])
            minutes = float(parts[1])
            return (hours + minutes/60) * 15  # Convert to degrees (15 degrees per hour)
        except:
            return None

    def convert_dec(dec_str):
        try:
            if pd.isna(dec_str):
                return None
            parts = dec_str.split()
            if len(parts) != 2:
                return None
            degrees = float(parts[0])
            minutes = float(parts[1])
            return degrees + minutes/60 * (1 if degrees >= 0 else -1)
        except:
            return None

    # Create standardized format
    result_df = pd.DataFrame({
        'name': df['Messier'].apply(lambda x: f"M{str(x).zfill(3)}"),  # M001 format
        'catalog': 'Messier',
        'ra': df['RA'].apply(convert_ra),
        'dec': df['DEC'].apply(convert_dec),
        'diameter': df['Messier'].apply(lambda x: diameter_data.get(x))
    })

    # Remove any rows with missing essential data or invalid coordinates
    result_df = result_df.dropna(subset=['name', 'ra', 'dec'])

    # Save processed data
    result_df.to_csv(output_file, index=False)

    print("\nData Processing Summary:")
    print(f"Total objects: {len(result_df)}")
    print("\nSample of processed data:")
    print(result_df.head())
    print("\nMissing values:")
    print(result_df.isnull().sum())

    return result_df

if __name__ == "__main__":
    data_dir = Path("/home/ubuntu/dso-search-api/dso-search-api/data")
    input_file = data_dir / "intermediate" / "messier.tsv"
    output_file = data_dir / "processed" / "processed_messier.csv"

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        exit(1)

    df = process_messier_data(input_file, output_file)
