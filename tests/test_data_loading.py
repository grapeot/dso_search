import pandas as pd
import glob
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_loading():
    """Test loading capability of all processed catalog data."""
    logger.info("Testing data loading capability...")
    
    total_objects = 0
    catalogs_info = []
    
    # Process each catalog file
    for file in glob.glob('data/processed_*.csv'):
        try:
            df = pd.read_csv(file)
            catalog = os.path.basename(file).replace('processed_', '').replace('.csv', '')
            
            # Gather statistics
            total_rows = len(df)
            with_diameter = df.diameter.notna().sum()
            with_coords = df[['ra', 'dec']].notna().all(axis=1).sum()
            
            catalogs_info.append({
                'catalog': catalog.upper(),
                'total': total_rows,
                'with_diameter': with_diameter,
                'with_coords': with_coords
            })
            
            total_objects += total_rows
            
            logger.info(f"{catalog.upper()}: {total_rows} objects")
            logger.info(f"  - With diameter: {with_diameter}")
            logger.info(f"  - With coordinates: {with_coords}")
            
        except Exception as e:
            logger.error(f"Error processing {file}: {str(e)}")
    
    # Print summary
    logger.info("\nSummary:")
    logger.info(f"Total objects across all catalogs: {total_objects}")
    logger.info("\nCatalog details:")
    
    # Create a formatted table
    fmt = "{:<10} {:<8} {:<8} {:<8}"
    logger.info(fmt.format("Catalog", "Total", "Diameter", "Coords"))
    logger.info("-" * 35)
    
    for info in catalogs_info:
        logger.info(fmt.format(
            info['catalog'],
            info['total'],
            info['with_diameter'],
            info['with_coords']
        ))

if __name__ == "__main__":
    test_data_loading()
