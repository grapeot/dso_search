import pandas as pd
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_ngc_catalog():
    url = "https://vizier.cds.unistra.fr/viz-bin/VizieR-4"
    params = {
        '-source': 'VII/118/ngc2000',
        '-out.form': 'TSV',
        '-out.max': '-1',  # No limit
        '-out': 'Name,RAJ2000,DEJ2000,Diam',
        '-out.meta': ''
    }

    logger.info("Downloading NGC catalog data...")
    response = requests.get(url, params=params)
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    lines = response.text.split('\n')
    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith('#'):
            data_start = i
            break

    if data_start >= len(lines):
        raise ValueError("No data found in VizieR response")

    header = lines[data_start]
    data_lines = [line for line in lines[data_start+1:] if line.strip() and not line.startswith('I')]

    with open("data/raw/ngc2000.tsv", "w") as f:
        f.write(header + '\n')
        f.write('\n'.join(data_lines))

    return len(data_lines)

def process_ngc_catalog():
    if not Path("data/raw/ngc2000.tsv").exists():
        num_objects = download_ngc_catalog()
        logger.info(f"Downloaded {num_objects} NGC objects")

    logger.info("Processing NGC catalog data...")
    df = pd.read_csv("data/raw/ngc2000.tsv", sep='\t', comment='#')

    processed_df = pd.DataFrame({
        'name': 'NGC' + df['Name'].astype(str).str.strip(),
        'catalog': 'NGC',
        'ra': pd.to_numeric(df['RAJ2000'], errors='coerce'),
        'dec': pd.to_numeric(df['DEJ2000'], errors='coerce'),
        'size': pd.to_numeric(df['Diam'], errors='coerce')
    })

    processed_df = processed_df.dropna(subset=['ra', 'dec'])

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    processed_df.to_csv('data/processed/processed_ngc.csv', index=False)
    logger.info(f"Processed {len(processed_df)} NGC objects")
    return processed_df

if __name__ == "__main__":
    process_ngc_catalog()
