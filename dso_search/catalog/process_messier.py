import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_messier_info():
    logger.info("Parsing Messier catalog info...")
    Path("data/intermediate").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    messier_data = []
    with open("data/raw/messier_catalog_info.txt", 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                fields = line.strip().split(',')
                if len(fields) >= 5:  # Ensure we have all required fields
                    obj = {
                        'name': fields[0].strip(),
                        'catalog': 'Messier',
                        'common_name': fields[1].strip(),
                        'ngc_name': fields[2].strip() if fields[2].strip() else None,
                        'size': 10.0  # Default size in arcminutes
                    }

                    try:
                        ra_str = fields[3].strip()
                        dec_str = fields[4].strip()

                        # Convert RA from HH:MM:SS.SS to decimal degrees (J2000)
                        ra_parts = ra_str.split(':')
                        if len(ra_parts) == 3:
                            ra_h = float(ra_parts[0])
                            ra_m = float(ra_parts[1])
                            ra_s = float(ra_parts[2])
                            ra = (ra_h + ra_m/60 + ra_s/3600) * 15  # Convert to degrees
                            obj['ra'] = round(ra, 6)

                        # Convert Dec from DD:MM:SS.S to decimal degrees (J2000)
                        dec_parts = dec_str.replace('+', '').split(':')
                        if len(dec_parts) == 3:
                            dec_sign = -1 if dec_str.startswith('-') else 1
                            dec_d = float(dec_parts[0])
                            dec_m = float(dec_parts[1])
                            dec_s = float(dec_parts[2])
                            dec = dec_d + dec_m/60 + dec_s/3600
                            dec *= dec_sign
                            obj['dec'] = round(dec, 6)

                        messier_data.append(obj)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing coordinates for {obj['name']}: {e}")
                        continue

    df = pd.DataFrame(messier_data)

    # Ensure all required columns are present
    required_columns = ['name', 'catalog', 'common_name', 'ngc_name', 'ra', 'dec', 'size']
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Missing required column: {col}")
            raise ValueError(f"Missing required column: {col}")

    # Save both intermediate and processed data
    df.to_csv("data/intermediate/messier_names.tsv", sep='\t', index=False)
    df.to_csv("data/processed/processed_messier.csv", index=False)

    logger.info(f"Processed {len(messier_data)} Messier objects")
    return len(messier_data)

def process_messier_catalog():
    logger.info("Processing Messier catalog data...")
    return parse_messier_info()

if __name__ == "__main__":
    process_messier_catalog()
