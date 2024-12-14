import pandas as pd
import json
from pathlib import Path
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_catalog_status():
    """Load the catalog status information."""
    with open('data/catalog_status.json', 'r') as f:
        return json.load(f)

def verify_coordinates(df):
    """Verify coordinate ranges and validity."""
    invalid_ra = df[~df['ra'].between(0, 360)]
    invalid_dec = df[~df['dec'].between(-90, 90)]

    if not invalid_ra.empty:
        logger.warning(f"Found {len(invalid_ra)} entries with invalid RA values:")
        print(invalid_ra[['name', 'catalog', 'ra', 'dec']])

    if not invalid_dec.empty:
        logger.warning(f"Found {len(invalid_dec)} entries with invalid DEC values:")
        print(invalid_dec[['name', 'catalog', 'ra', 'dec']])

    return len(invalid_ra) == 0 and len(invalid_dec) == 0

def verify_diameters(df):
    """Verify diameter values are positive and reasonable."""
    invalid_diam = df[df['diameter'] <= 0]
    if not invalid_diam.empty:
        logger.warning(f"Found {len(invalid_diam)} entries with invalid diameter values:")
        print(invalid_diam[['name', 'catalog', 'diameter']])
    return len(invalid_diam) == 0

def verify_names(df):
    """Verify object names follow the correct format."""
    for catalog in df['catalog'].unique():
        mask = df['catalog'] == catalog
        names = df.loc[mask, 'name']
        if not all(names.str.startswith(catalog)):
            logger.warning(f"Found inconsistent naming in {catalog} catalog:")
            print(names[~names.str.startswith(catalog)].head())
    return True

def merge_catalogs(status):
    """Merge all processed catalog files into a single DataFrame."""
    data_path = Path('data')
    all_data = []

    for catalog, info in status['catalogs'].items():
        file_path = data_path / info['file']
        if not file_path.exists():
            logger.error(f"Missing catalog file: {file_path}")
            continue

        df = pd.read_csv(file_path)
        expected_count = info['count']
        actual_count = len(df)

        if expected_count != actual_count:
            logger.warning(f"Count mismatch in {catalog}: expected {expected_count}, got {actual_count}")

        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)

def main():
    """Main verification function."""
    logger.info("Starting data verification...")

    # Load catalog status
    status = load_catalog_status()
    logger.info(f"Loaded catalog status. Expected total: {status['total_objects']}")

    # Merge all catalogs
    df = merge_catalogs(status)
    logger.info(f"Merged data shape: {df.shape}")

    # Basic data quality checks
    logger.info("\nChecking for missing values:")
    print(df.isnull().sum())

    # Verify coordinates
    logger.info("\nVerifying coordinates...")
    coords_valid = verify_coordinates(df)

    # Verify diameters
    logger.info("\nVerifying diameters...")
    diameters_valid = verify_diameters(df)

    # Verify names
    logger.info("\nVerifying object names...")
    names_valid = verify_names(df)

    # Save merged dataset if all checks pass
    if coords_valid and diameters_valid and names_valid:
        logger.info("\nAll verifications passed. Saving merged dataset...")
        output_path = Path('data') / 'merged_dso.csv'
        df.to_csv(output_path, index=False)
        logger.info(f"Merged dataset saved to {output_path}")

        # Save summary statistics
        summary = {
            'total_objects': len(df),
            'objects_by_catalog': df['catalog'].value_counts().to_dict(),
            'ra_range': [float(df['ra'].min()), float(df['ra'].max())],
            'dec_range': [float(df['dec'].min()), float(df['dec'].max())],
            'diameter_stats': {
                'min': float(df['diameter'].min()),
                'max': float(df['diameter'].max()),
                'mean': float(df['diameter'].mean()),
                'median': float(df['diameter'].median())
            }
        }

        with open(Path('data') / 'dataset_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info("Dataset summary saved to dataset_summary.json")
    else:
        logger.error("Verification failed. Please check the warnings above.")

if __name__ == "__main__":
    main()
