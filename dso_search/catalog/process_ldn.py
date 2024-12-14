import pandas as pd
import numpy as np
from pathlib import Path
import requests

def download_ldn_data(output_file):
    """Download Lynds Dark Nebulae catalog data from VizieR"""
    url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv'
    params = {
        '-source': 'VII/7A/ldn',
        '-out.max': 'unlimited',
        '-out.form': 'TSV',
        '-out.meta': '',
        '-out': ['LDN', 'RAJ2000', 'DEJ2000', 'Area', 'Opacity']
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

def process_ldn_data(input_file, output_file):
    """Process Lynds Dark Nebulae catalog data into standardized format"""
    print(f"Processing LDN data from {input_file}")

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
            if len(parts) >= 5:  # We need LDN, RA, DEC, Area, and Opacity
                ldn, raj2000, dej2000, area, opacity = parts[:5]
                data.append({
                    'LDN': ldn.strip(),
                    'RAJ2000': raj2000.strip(),
                    'DEJ2000': dej2000.strip(),
                    'Area': area.strip(),
                    'Opacity': opacity.strip()
                })

    # Create DataFrame
    df = pd.DataFrame(data)
    print("\nRaw data sample:")
    print(df.head())

    # Clean up the data
    df = df.replace('', np.nan)  # Replace empty strings with NaN
    df = df.dropna(subset=['LDN', 'RAJ2000', 'DEJ2000'])  # Remove rows with missing essential data

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

    # Calculate diameter from area (assuming circular shape)
    def area_to_diameter(area):
        if pd.isna(area):
            return np.nan
        try:
            area_val = float(area)
            if area_val <= 0:
                return np.nan  # Invalid area, return NaN instead of 0
            # Area is in square degrees, convert to square arcminutes
            area_arcmin = area_val * 3600  # 1 deg² = 3600 arcmin²
            # For a circle: area = π * (diameter/2)²
            # Therefore: diameter = 2 * sqrt(area/π)
            diameter_arcmin = 2 * np.sqrt(area_arcmin / np.pi)
            return diameter_arcmin
        except Exception as e:
            print(f"Error converting area {area}: {e}")
            return np.nan

    # Create standardized format
    result_df = pd.DataFrame({
        'name': df['LDN'].apply(lambda x: f"LDN{str(x).strip().zfill(4)}" if pd.notna(x) else None),
        'catalog': 'LDN',
        'ra': df['RAJ2000'].apply(lambda x: sex_to_deg(x, is_ra=True)),
        'dec': df['DEJ2000'].apply(lambda x: sex_to_deg(x, is_ra=False)),
        'diameter': df['Area'].apply(area_to_diameter)  # Convert area to diameter in arcmin
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

    input_file = data_dir / "ldn.tsv"
    output_file = data_dir / "processed_ldn.csv"

    # Download data if it doesn't exist
    if not input_file.exists():
        print("Downloading LDN catalog data...")
        if not download_ldn_data(input_file):
            print("Error downloading data!")
            exit(1)

    df = process_ldn_data(input_file, output_file)
