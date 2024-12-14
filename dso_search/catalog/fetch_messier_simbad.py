import pandas as pd
import logging
from pathlib import Path
import time
from astroquery.simbad import Simbad

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_messier_diameters():
    """Fetch Messier object diameters from SIMBAD."""
    logger.info("Fetching Messier object diameters from SIMBAD...")

    try:
        # Configure Simbad query with specific fields
        customSimbad = Simbad()
        # Clear existing fields and add only what we need
        customSimbad.remove_votable_fields('*')
        customSimbad.add_votable_fields('dim_majaxis', 'dim_minaxis')

        # Read existing Messier data to get object names
        existing_df = pd.read_csv('data/processed_messier.csv')

        data = []
        for _, row in existing_df.iterrows():
            try:
                messier_name = row['name'].replace('M', 'M ')  # SIMBAD format
                result_table = customSimbad.query_object(messier_name)

                if result_table is not None and len(result_table) > 0:
                    major_axis = result_table['DIM_MAJAXIS'][0]
                    minor_axis = result_table['DIM_MINAXIS'][0]

                    if major_axis and major_axis != '':
                        try:
                            major = float(major_axis)
                            minor = float(minor_axis) if minor_axis and minor_axis != '' else major
                            # Use larger dimension
                            diameter = max(major, minor)

                            data.append({
                                'name': row['name'],
                                'diameter': diameter
                            })
                            logger.info(f"Found diameter for {row['name']}: {diameter} arcmin")
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse dimensions for {row['name']}")
                    else:
                        logger.warning(f"No dimensions found for {row['name']}")

                # Add delay to avoid overwhelming the service
                time.sleep(1)

            except Exception as e:
                logger.warning(f"Error processing {row['name']}: {str(e)}")
                continue

        # Create DataFrame with diameter data
        diameter_df = pd.DataFrame(data)

        if diameter_df.empty:
            raise ValueError("No valid data could be parsed from SIMBAD")

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
