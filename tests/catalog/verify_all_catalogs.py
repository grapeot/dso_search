import pandas as pd
import numpy as np
from pathlib import Path
import logging
from astropy.coordinates import SkyCoord
import astropy.units as u

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_catalog(catalog_name):
    """Load a processed catalog CSV file."""
    try:
        df = pd.read_csv(f"data/processed_{catalog_name.lower()}.csv")
        return df
    except Exception as e:
        logger.error(f"Error loading {catalog_name}: {e}")
        return None

def verify_coordinates(df, catalog_name):
    """Verify coordinate ranges and validity."""
    logger.info(f"\nVerifying coordinates for {catalog_name}:")

    # Check RA range (0 to 360)
    ra_range = df['ra'].between(0, 360)
    logger.info(f"RA in valid range: {ra_range.all()}")
    if not ra_range.all():
        logger.warning(f"Found {(~ra_range).sum()} RA values outside 0-360 range")

    # Check DEC range (-90 to +90)
    dec_range = df['dec'].between(-90, 90)
    logger.info(f"DEC in valid range: {dec_range.all()}")
    if not dec_range.all():
        logger.warning(f"Found {(~dec_range).sum()} DEC values outside -90/+90 range")

def verify_required_fields(df, catalog_name):
    """Verify presence and validity of required fields."""
    required_fields = ['name', 'ra', 'dec', 'diameter', 'catalog']
    missing_fields = [field for field in required_fields if field not in df.columns]

    if missing_fields:
        logger.error(f"{catalog_name} missing required fields: {missing_fields}")
        return False

    # Check for null values
    null_counts = df[required_fields].isnull().sum()
    logger.info(f"\n{catalog_name} null value counts:")
    print(null_counts)

    return True

def main():
    catalogs = [
        'NGC', 'IC', 'Abell', 'LBN', 'LDN', 'Sharpless',
        'Barnard', 'Caldwell', 'Messier', 'VdB'
    ]

    total_objects = 0
    all_data = []

    logger.info("Starting catalog verification...")

    for catalog in catalogs:
        df = load_catalog(catalog)
        if df is None:
            continue

        logger.info(f"\n=== {catalog} Catalog ===")
        logger.info(f"Records: {len(df)}")
        total_objects += len(df)

        verify_required_fields(df, catalog)
        verify_coordinates(df, catalog)

        # Sample some records
        logger.info(f"\nSample records from {catalog}:")
        print(df.head(2))

        all_data.append(df)

    # Combine all data for overall statistics
    combined_df = pd.concat(all_data, ignore_index=True)

    logger.info("\n=== Overall Statistics ===")
    logger.info(f"Total objects across all catalogs: {total_objects}")
    logger.info(f"Unique objects in combined dataset: {len(combined_df)}")
    logger.info("\nMissing values in combined dataset:")
    print(combined_df.isnull().sum())

    # Check for duplicate names
    duplicates = combined_df['name'].value_counts()
    if (duplicates > 1).any():
        logger.warning("\nFound duplicate object names:")
        print(duplicates[duplicates > 1].head())

if __name__ == "__main__":
    main()
