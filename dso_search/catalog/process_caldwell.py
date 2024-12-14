import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caldwell to NGC/IC mapping
CALDWELL_MAP = {
    'C1': 'IC 1613',
    'C2': 'NGC 40',
    'C3': 'NGC 4236',
    'C4': 'NGC 7023',
    'C5': 'IC 342',
    'C6': 'NGC 6543',
    'C7': 'NGC 2403',
    'C8': 'NGC 559',
    'C9': 'NGC 7331',
    'C10': 'NGC 663',
    'C11': 'NGC 7635',
    'C12': 'NGC 6946',
    'C13': 'NGC 457',
    'C14': 'NGC 869/884',  # Double Cluster
    'C15': 'NGC 6826',
    'C16': 'NGC 7243',
    'C17': 'NGC 147',
    'C18': 'NGC 185',
    'C19': 'IC 5146',
    'C20': 'NGC 7000',
    'C21': 'NGC 4449',
    'C22': 'NGC 7662',
    'C23': 'NGC 891',
    'C24': 'NGC 1275',
    'C25': 'NGC 2419',
    'C26': 'NGC 4244',
    'C27': 'NGC 6888',
    'C28': 'NGC 752',
    'C29': 'NGC 5005',
    'C30': 'NGC 7331',
    'C31': 'IC 405',
    'C32': 'NGC 4631',
    'C33': 'NGC 6992/5',
    'C34': 'NGC 6960',
    'C35': 'NGC 4889',
    'C36': 'NGC 4559',
    'C37': 'NGC 6885',
    'C38': 'NGC 4565',
    'C39': 'NGC 2392',
    'C40': 'NGC 3626',
    'C41': 'NGC 3242',
    'C42': 'NGC 7006',
    'C43': 'NGC 7814',
    'C44': 'NGC 7479',
    'C45': 'NGC 5248',
    'C46': 'NGC 2261',
    'C47': 'NGC 6934',
    'C48': 'NGC 2775',
    'C49': 'NGC 2237-9',
    'C50': 'NGC 2244',
    'C51': 'IC 1613',
    'C52': 'NGC 4697',
    'C53': 'NGC 3115',
    'C54': 'NGC 2506',
    'C55': 'NGC 7009',
    'C56': 'NGC 246',
    'C57': 'NGC 6822',
    'C58': 'NGC 2360',
    'C59': 'NGC 3242',
    'C60': 'NGC 4038',
    'C61': 'NGC 4039',
    'C62': 'NGC 247',
    'C63': 'NGC 7293',
    'C64': 'NGC 2613',
    'C65': 'NGC 253',
    'C66': 'NGC 5694',
    'C67': 'NGC 1097',
    'C68': 'NGC 6729',
    'C69': 'NGC 6302',
    'C70': 'NGC 300',
    'C71': 'NGC 2477',
    'C72': 'NGC 55',
    'C73': 'NGC 1851',
    'C74': 'NGC 3132',
    'C75': 'NGC 6124',
    'C76': 'NGC 6231',
    'C77': 'NGC 5128',
    'C78': 'NGC 6541',
    'C79': 'NGC 3201',
    'C80': 'NGC 5139',
    'C81': 'NGC 6352',
    'C82': 'NGC 6193',
    'C83': 'NGC 4945',
    'C84': 'NGC 5286',
    'C85': 'IC 2391',
    'C86': 'NGC 6397',
    'C87': 'NGC 1261',
    'C88': 'NGC 5823',
    'C89': 'NGC 6087',
    'C90': 'NGC 2867',
    'C91': 'NGC 3532',
    'C92': 'NGC 3372',
    'C93': 'NGC 6752',
    'C94': 'NGC 4755',
    'C95': 'NGC 6025',
    'C96': 'NGC 2516',
    'C97': 'NGC 3766',
    'C98': 'NGC 4609',
    'C99': 'NGC 5011',
    'C100': 'IC 2944',
    'C101': 'NGC 6744',
    'C102': 'IC 2602',
    'C103': 'NGC 2070',
    'C104': 'NGC 362',
    'C105': 'NGC 4833',
    'C106': 'NGC 104',
    'C107': 'NGC 6101',
    'C108': 'NGC 4372',
    'C109': 'NGC 3195'
}

def process_caldwell_data(ngc_file, ic_file):
    """Process Caldwell objects using NGC/IC data."""
    logger.info("Processing Caldwell catalog data using NGC/IC mappings")

    try:
        # Read NGC and IC data
        ngc_df = pd.read_csv(ngc_file)
        ic_df = pd.read_csv(ic_file)

        # Create empty DataFrame for Caldwell objects
        caldwell_df = pd.DataFrame(columns=['name', 'catalog', 'ra', 'dec', 'diameter'])

        # Process each Caldwell object
        for caldwell_id, ngc_id in CALDWELL_MAP.items():
            try:
                # Handle special cases with multiple objects
                if '/' in ngc_id:
                    # Handle double clusters like NGC 869/884
                    primary_id = ngc_id.split('/')[0]
                elif '-' in ngc_id:
                    # Handle ranges like NGC 2237-9
                    base_num = ngc_id.replace('NGC ', '')
                    start_num = base_num.split('-')[0]
                    end_suffix = base_num.split('-')[1]
                    # Reconstruct the full end number (e.g., 2237-9 -> 2239)
                    end_num = start_num[:-len(end_suffix)] + end_suffix
                    # Use the first number in the range
                    primary_id = f"NGC {start_num}"
                else:
                    primary_id = ngc_id

                # Determine if it's NGC or IC
                if primary_id.startswith('NGC'):
                    number = int(primary_id.replace('NGC ', ''))
                    source_df = ngc_df
                    source_df = source_df[source_df['name'] == f"NGC{str(number).zfill(4)}"]
                else:  # IC object
                    number = int(primary_id.replace('IC ', ''))
                    source_df = ic_df
                    # Try both formats (with and without space)
                    source_df = source_df[source_df['name'].isin([f"IC{str(number).zfill(4)}", f"I{str(number).zfill(4)}"])]

                if len(source_df) > 0:
                    # Use the first match if multiple exist
                    obj_data = source_df.iloc[0]
                    caldwell_df = pd.concat([caldwell_df, pd.DataFrame([{
                        'name': f"C{caldwell_id[1:].zfill(3)}",  # C001 format
                        'catalog': 'Caldwell',
                        'ra': obj_data['ra'],
                        'dec': obj_data['dec'],
                        'diameter': obj_data['diameter']
                    }])], ignore_index=True)
                else:
                    logger.warning(f"Could not find {ngc_id} for {caldwell_id}")

            except Exception as e:
                logger.error(f"Error processing {caldwell_id} ({ngc_id}): {str(e)}")
                continue

        # Remove any rows with missing values
        caldwell_df = caldwell_df.dropna()

        logger.info("\nData Processing Summary:")
        logger.info(f"Total objects: {len(caldwell_df)}")
        logger.info("\nSample of processed data:")
        print(caldwell_df.head())
        logger.info("\nMissing values:")
        print(caldwell_df.isnull().sum())

        # Save processed data
        output_path = Path("data") / "processed_caldwell.csv"
        caldwell_df.to_csv(output_path, index=False)
        logger.info(f"\nProcessed data saved to {output_path}")

        return caldwell_df

    except Exception as e:
        logger.error(f"Error processing Caldwell data: {str(e)}")
        raise

if __name__ == "__main__":
    ngc_file = Path("data") / "processed_ngc.csv"
    ic_file = Path("data") / "processed_ic.csv"

    if not ngc_file.exists() or not ic_file.exists():
        logger.error("NGC/IC processed data files not found. Please process NGC/IC catalogs first.")
        exit(1)

    process_caldwell_data(ngc_file, ic_file)
