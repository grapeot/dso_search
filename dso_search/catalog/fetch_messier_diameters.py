import pandas as pd
import requests
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_messier_diameters():
    """Fetch Messier object diameters from VizieR."""
    logger.info("Fetching Messier object diameters from VizieR...")

    try:
        # VizieR base URL
        url = 'https://vizier.cds.unistra.fr/viz-bin/asu-tsv'

        # Parameters for the query - using catalog VII/1B/messier
        params = {
            '-source': 'VII/1B/messier',
            '-out.max': 'unlimited',
            '-out.form': 'TSV',
            '-out.meta': 'true',
            '-out': 'Messier MType Size',  # Messier number, type, and size
            '-oc.form': '1'
        }

        logger.info(f"Querying VizieR with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Save raw response for inspection
        with open('data/messier_raw.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)

        # Process the TSV data
        lines = [line for line in response.text.strip().split('\n')
                if line and not line.startswith('#')]

        if not lines:
            raise ValueError("No data found in response")

        # Create DataFrame from the data portion
        data = []
        for line in lines[1:]:  # Skip header row
            try:
                fields = line.strip().split('\t')
                if len(fields) >= 3:
                    num, mtype, size = fields[0], fields[1], fields[2]
                    num = num.strip()
                    size = size.strip()

                    if num and size and size != '':
                        try:
                            size_val = float(size)
                            data.append({
                                'name': f"M{num.zfill(3)}",
                                'diameter': size_val
                            })
                        except ValueError:
                            logger.warning(f"Could not convert size '{size}' to float for M{num}")
                            continue
            except ValueError as e:
                logger.warning(f"Error parsing line '{line}': {str(e)}")
                continue

        # Create DataFrame with diameter data
        diameter_df = pd.DataFrame(data)

        if diameter_df.empty:
            raise ValueError("No valid data could be parsed from the response")

        # Read existing Messier data
        existing_df = pd.read_csv('data/processed_messier.csv')

        # Merge diameter data with existing data
        merged_df = existing_df.merge(diameter_df[['name', 'diameter']], on='name', how='left')

        # Save updated data
        output_path = Path('data') / 'processed_messier.csv'
        merged_df.to_csv(output_path, index=False)

        logger.info(f"\nProcessing complete:")
        logger.info(f"Total objects: {len(merged_df)}")
        logger.info(f"Objects with diameter data: {merged_df['diameter'].notna().sum()}")
        if merged_df['diameter'].notna().any():
            logger.info(f"Diameter range: {merged_df['diameter'].min():.1f} to {merged_df['diameter'].max():.1f} arcmin")

        return merged_df

    except Exception as e:
        logger.error(f"Error processing Messier data: {e}")
        raise

if __name__ == "__main__":
    fetch_messier_diameters()
