import pandas as pd
import numpy as np
from pathlib import Path
import requests
import logging
from astropy.coordinates import SkyCoord
from astropy import units as u

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_vdb_data():
    """Download van den Bergh catalog data from VizieR."""
    url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv'
    params = {
        '-source': 'VII/21/catalog',
        '-out.max': 'unlimited',
        '-out.form': 'TSV',
        '-out.meta': 'true',
        '-out': 'VdB _RA _DE BRadMax RRadMax',
        '-oc.form': '1'
    }

    logger.info("Downloading van den Bergh catalog data...")
    logger.info(f"Downloading from VizieR with params: {params}")

    response = requests.get(url, params=params)
    logger.info(f"Response status: {response.status_code}")

    if response.status_code == 200:
        data_path = Path("data")
        data_path.mkdir(exist_ok=True)

        # Save raw response for inspection
        with open(data_path / "vdb_raw.txt", "w", encoding="utf-8") as f:
            f.write(response.text)

        logger.info("Raw response saved to vdb_raw.txt")

        # Write processed TSV
        with open(data_path / "vdb.tsv", "w", encoding="utf-8") as f:
            f.write(response.text)

        return data_path / "vdb.tsv"
    else:
        raise Exception(f"Failed to download data: {response.status_code}")

def process_vdb_data(file_path):
    """Process van den Bergh catalog data."""
    logger.info(f"Processing van den Bergh data from {file_path}")

    try:
        # Read the TSV file, skipping metadata lines that start with #
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Find the first non-comment line (this will be our header)
        data_start = 0
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                data_start = i
                break

        # Create DataFrame from the data portion
        data_lines = [line.strip().split('\t') for line in lines[data_start:] if line.strip()]
        columns = ['VdB', '_RA', '_DE', 'BRadMax', 'RRadMax']
        df = pd.DataFrame(data_lines[1:], columns=columns)  # Skip header row

        # Create processed DataFrame
        processed_df = pd.DataFrame()

        # Process VdB numbers into names
        processed_df['name'] = df['VdB'].apply(lambda x: f"VdB{str(x).strip().zfill(4)}" if pd.notna(x) else None)
        processed_df['catalog'] = 'VdB'

        # Convert coordinates to numeric values (already in J2000)
        processed_df['ra'] = pd.to_numeric(df['_RA'], errors='coerce')
        processed_df['dec'] = pd.to_numeric(df['_DE'], errors='coerce')

        # Convert radii to numeric values and handle missing values
        blue_radius = pd.to_numeric(df['BRadMax'], errors='coerce')
        red_radius = pd.to_numeric(df['RRadMax'], errors='coerce')

        # Calculate diameter using the maximum of available measurements
        # Multiply by 2 to convert radius to diameter
        processed_df['diameter'] = 2 * pd.DataFrame([blue_radius, red_radius]).max()

        # Use a conservative default of 2 arcmin only when no measurements available
        processed_df['diameter'] = processed_df['diameter'].fillna(2.0)

        # Remove any rows with invalid coordinates
        processed_df = processed_df.dropna(subset=['ra', 'dec'])

        # Save processed data
        output_file = Path(file_path).parent / 'processed_vdb.csv'
        processed_df.to_csv(output_file, index=False)

        # Log statistics
        logger.info(f"\nProcessing complete:")
        logger.info(f"Total objects: {len(processed_df)}")
        logger.info(f"Objects with measured diameters: {(processed_df['diameter'] != 2.0).sum()}")
        logger.info(f"Objects using default diameter: {(processed_df['diameter'] == 2.0).sum()}")
        logger.info(f"Diameter range: {processed_df['diameter'].min():.1f} to {processed_df['diameter'].max():.1f} arcmin")

        return output_file

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise

if __name__ == "__main__":
    data_file = download_vdb_data()
    process_vdb_data(data_file)
