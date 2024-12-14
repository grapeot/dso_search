import pandas as pd
import numpy as np
from pathlib import Path
import requests

def download_barnard_data(output_file):
    """Download Barnard catalog data from VizieR"""
    url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv'
    params = {
        '-source': 'VII/220A/barnard',
        '-out.max': 'unlimited',
        '-out.form': 'TSV',
        '-out.meta': '',
        '-out': ['Barn', 'RA1875', 'DE1875', 'Diam']
    }

    print("Downloading from VizieR with params:", params)
    response = requests.get(url, params=params)
    print("Response status:", response.status_code)

    if response.status_code == 200:
        print("Sample of received data:")
        lines = response.text.split('\n')[:10]
        for line in lines:
            print(line)

    with open(output_file, 'w') as f:
        f.write(response.text)

    return response.status_code == 200

def process_barnard_data(input_file, output_file):
    """Process Barnard Dark Nebulae catalog data into standardized format"""
    print(f"Processing Barnard data from {input_file}")

    # Read TSV file, skipping initial comments
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Find where the actual data starts (after headers)
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('#'):
            data_start = i
            break

    print(f"Data starts at line {data_start}")

    # Process data lines manually
    data = []
    for line in lines[data_start:]:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split('\t')
            if len(parts) >= 4:  # We need Barnard number, RA, DEC, and diameter
                barn, ra1875, de1875, diam = parts[:4]
                data.append({
                    'Barn': barn.strip(),
                    'RA1875': ra1875.strip(),
                    'DE1875': de1875.strip(),
                    'Diam': diam.strip()
                })

    # Create DataFrame
    df = pd.DataFrame(data)
    print("\nRaw data sample:")
    print(df.head())

    # Clean up the data
    df = df.replace('', np.nan)  # Replace empty strings with NaN
    df = df.dropna(subset=['Barn', 'RA1875', 'DE1875'])  # Remove rows with missing essential data

    # Convert coordinates from sexagesimal to decimal degrees
    def sex_to_deg(value, is_ra=True):
        if pd.isna(value):
            return np.nan
        try:
            # Handle different formats of coordinates
            parts = str(value).replace(':', ' ').split()
            if len(parts) < 2:
                return pd.to_numeric(value, errors='coerce')

            if is_ra:
                # RA format: HH MM SS.S
                h = float(parts[0])
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                return 15 * (h + m/60 + s/3600)  # Convert hours to degrees
            else:
                # DEC format: DD MM SS.S
                d = float(parts[0])
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                sign = -1 if d < 0 else 1
                return sign * (abs(d) + m/60 + s/3600)
        except Exception as e:
            print(f"Error converting coordinate {value}: {e}")
            return np.nan

    # Create standardized format
    result_df = pd.DataFrame({
        'name': df['Barn'].apply(lambda x: f"B{str(x).zfill(3)}" if pd.notna(x) else None),  # B001 format
        'catalog': 'Barnard',
        'ra': df['RA1875'].apply(lambda x: sex_to_deg(x, is_ra=True)),
        'dec': df['DE1875'].apply(lambda x: sex_to_deg(x, is_ra=False)),
        'diameter': pd.to_numeric(df['Diam'], errors='coerce')  # Already in arcmin
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
    data_dir.mkdir(parents=True, exist_ok=True)

    input_file = data_dir / "barnard.tsv"
    output_file = data_dir / "processed_barnard.csv"

    # Download data if it doesn't exist
    if not input_file.exists():
        print("Downloading Barnard catalog data...")
        if not download_barnard_data(input_file):
            print("Error downloading data!")
            exit(1)

    df = process_barnard_data(input_file, output_file)
