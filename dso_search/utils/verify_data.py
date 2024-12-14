"""Verify processed catalog data structure and content."""
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_processed_data():
    """Verify the structure and content of processed catalog data."""
    try:
        df = pd.read_csv('data/processed/processed_messier.csv')

        logger.info("\nSample of processed data:")
        print(df[['name', 'ra', 'dec', 'size']].head())

        logger.info("\nData types:")
        print(df.dtypes)

        logger.info("\nMissing values:")
        print(df.isnull().sum())

        # Verify coordinate ranges
        ra_valid = (df['ra'] >= 0) & (df['ra'] < 360)
        dec_valid = (df['dec'] >= -90) & (df['dec'] <= 90)

        if not ra_valid.all():
            logger.error("Invalid RA values found!")
        if not dec_valid.all():
            logger.error("Invalid Dec values found!")

        return all(ra_valid) and all(dec_valid)

    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False

if __name__ == "__main__":
    verify_processed_data()
