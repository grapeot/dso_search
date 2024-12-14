import pandas as pd
import numpy as np
from pathlib import Path
import requests
from astropy.coordinates import SkyCoord
from astropy import units as u

def download_sharpless_data(output_file):
    url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv'
    params = {
        '-source': 'VII/20/catalog',
        '-out.max': 'unlimited',
        '-out.form': 'TSV',
        '-out.meta': '',
        '-out': ['Sh2', 'RA1900', 'DE1900', 'Diam']
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

def process_sharpless_data(input_file, output_file):
    print(f"Processing Sharpless data from {input_file}")

    with open(input_file, 'r') as f:
        lines = f.readlines()

    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('#'):
            data_start = i
            break

    print(f"Data starts at line {data_start}")

    data = []
    for line in lines[data_start:]:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                sh2, ra1900, de1900, diam = parts[:4]
                data.append({
                    'Sh2': sh2.strip(),
                    'RA1900': ra1900.strip(),
                    'DE1900': de1900.strip(),
                    'Diam': diam.strip()
                })

    df = pd.DataFrame(data)
    print("\nRaw data sample:")
    print(df.head())

    df = df.replace('', np.nan)
    df = df.dropna(subset=['Sh2', 'RA1900', 'DE1900'])

    def sex_to_deg(value, is_ra=True):
        if pd.isna(value):
            return np.nan
        try:
            parts = str(value).replace(':', ' ').split()
            if len(parts) < 2:
                return pd.to_numeric(value, errors='coerce')

            if is_ra:
                h = float(parts[0])
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                return 15 * (h + m/60 + s/3600)
            else:
                d = float(parts[0])
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                sign = -1 if d < 0 else 1
                return sign * (abs(d) + m/60 + s/3600)
        except Exception as e:
            print(f"Error converting coordinate {value}: {e}")
            return np.nan

    # Convert 1900 coordinates to decimal degrees
    ra_1900 = df['RA1900'].apply(lambda x: sex_to_deg(x, is_ra=True))
    dec_1900 = df['DE1900'].apply(lambda x: sex_to_deg(x, is_ra=False))

    # Convert from 1900 to J2000 using astropy
    coords_1900 = SkyCoord(ra=ra_1900, dec=dec_1900,
                          unit=(u.degree, u.degree),
                          frame='fk4',
                          equinox='B1900.0')
    coords_j2000 = coords_1900.transform_to('fk5')

    result_df = pd.DataFrame({
        'name': df['Sh2'].apply(lambda x: f"Sh2-{str(x).zfill(3)}" if pd.notna(x) else None),
        'catalog': 'Sharpless',
        'ra': coords_j2000.ra.degree,
        'dec': coords_j2000.dec.degree,
        'diameter': pd.to_numeric(df['Diam'], errors='coerce')
    })

    result_df = result_df.dropna(subset=['name', 'ra', 'dec'])

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

    input_file = data_dir / "sharpless.tsv"
    output_file = data_dir / "processed_sharpless.csv"

    if not input_file.exists():
        print("Downloading Sharpless catalog data...")
        if not download_sharpless_data(input_file):
            print("Error downloading data!")
            exit(1)

    df = process_sharpless_data(input_file, output_file)
