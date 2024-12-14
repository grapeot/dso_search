import requests
import pandas as pd
import logging
from pathlib import Path
import math
from astropy.coordinates import SkyCoord
from astropy import units as u

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_lbn_data():
    """Download LBN (Lynds Bright Nebulae) catalog data from VizieR."""
    base_url = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv"

    # Request all columns at once
    params = {
        '-source': 'VII/9/catalog',
        '-out.max': 'unlimited',
        '-out.form': 'TSV',
        '-out.meta': '',
        '-out': ['Seq', 'RA1950', 'DE1950', 'Diam1', 'Diam2']
    }

    logger.info("Downloading LBN catalog data...")
    logger.info(f"Downloading from VizieR with params: {params}")

    # Convert list parameters to comma-separated string
    for key, value in params.items():
        if isinstance(value, list):
            params[key] = ','.join(value)

    response = requests.get(base_url, params=params)
    logger.info(f"Response status: {response.status_code}")

    if response.status_code == 200:
        data_path = Path("data")
        data_path.mkdir(exist_ok=True)

        # Save raw response for inspection
        with open(data_path / "lbn_raw.txt", "w", encoding="utf-8") as f:
            f.write(response.text)

        logger.info("Raw response saved to lbn_raw.txt")
        logger.info("Sample of received data:")
        print(response.text[:500])

        # Process the TSV data
        lines = response.text.split('\n')
        header = None
        data_lines = []

        for line in lines:
            if line.startswith('#'):
                continue
            if header is None:
                header = line.strip()
                continue
            if line.strip():
                data_lines.append(line)

        # Write processed TSV
        with open(data_path / "lbn.tsv", "w", encoding="utf-8") as f:
            f.write(header + '\n')
            f.write('\n'.join(data_lines))

        return data_path / "lbn.tsv"
    else:
        raise Exception(f"Failed to download data: {response.status_code}")

def sex_to_deg(value, is_ra=True):
    """Convert sexagesimal coordinates to decimal degrees."""
    try:
        if isinstance(value, (int, float)):
            return float(value)

        # Handle space-separated format and add seconds if missing
        parts = value.strip().split()
        if len(parts) == 2:  # Only hours and minutes provided
            parts.append('0')  # Add zero seconds
        elif len(parts) != 3:
            return None

        h = float(parts[0])
        m = float(parts[1])
        s = float(parts[2])

        if h < 0:
            m = -m
            s = -s

        deg = abs(h) + m/60 + s/3600

        if h < 0:
            deg = -deg

        # Convert RA from hours to degrees if needed
        if is_ra:
            deg *= 15

        return deg
    except (ValueError, AttributeError, TypeError) as e:
        logger.error(f"Error converting coordinate {value}: {str(e)}")
        return None

def process_lbn_data(file_path):
    """Process the LBN catalog data."""
    logger.info(f"Processing LBN data from {file_path}")

    try:
        # Read raw file first to inspect
        with open(file_path, 'r') as f:
            content = f.read()
            logger.info("Raw TSV content sample:")
            print(content[:1000])

        # Read the TSV file with explicit parameters
        df = pd.read_csv(file_path, sep='\t', na_values=['----', '', ' '])

        logger.info("\nRaw data sample:")
        print(df.head())
        print("\nColumns:", df.columns.tolist())

        # Create standardized DataFrame
        processed_df = pd.DataFrame()

        # Map the unnamed columns to their correct names
        column_mapping = {
            '----': 'Seq',
            '-----': 'RA1950',
            '------': 'DE1950',
            '----.1': 'Diam1',
            '---': 'Diam2'
        }
        df = df.rename(columns=column_mapping)

        # Process each row
        processed_df['name'] = df['Seq'].apply(lambda x: f"LBN{str(x).strip().zfill(4)}" if pd.notna(x) else None)
        processed_df['catalog'] = 'LBN'

        # Convert B1950 coordinates to decimal degrees
        ra_b1950 = df['RA1950'].apply(lambda x: sex_to_deg(x, is_ra=True))
        dec_b1950 = df['DE1950'].apply(lambda x: sex_to_deg(x, is_ra=False))

        # Convert from B1950 to J2000 using astropy
        coords_b1950 = SkyCoord(ra=ra_b1950, dec=dec_b1950,
                               unit=(u.degree, u.degree),
                               frame='fk4',
                               equinox='B1950.0')
        coords_j2000 = coords_b1950.transform_to('fk5')

        # Store J2000 coordinates
        processed_df['ra'] = coords_j2000.ra.degree
        processed_df['dec'] = coords_j2000.dec.degree

        # Use the larger diameter (Diam1) for consistency
        processed_df['diameter'] = pd.to_numeric(df['Diam1'], errors='coerce')

        # Remove any rows with missing values
        processed_df = processed_df.dropna()

        logger.info("\nData Processing Summary:")
        logger.info(f"Total objects: {len(processed_df)}")

        logger.info("\nSample of processed data:")
        print(processed_df.head())

        logger.info("\nMissing values:")
        print(processed_df.isnull().sum())

        # Save processed data
        output_path = Path("data") / "processed_lbn.csv"
        processed_df.to_csv(output_path, index=False)
        logger.info(f"\nProcessed data saved to {output_path}")

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise

if __name__ == "__main__":
    data_file = download_lbn_data()
    process_lbn_data(data_file)
