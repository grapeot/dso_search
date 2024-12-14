import pandas as pd
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_messier_names():
    url = "https://vizier.cds.unistra.fr/viz-bin/VizieR-4"
    params = {
        '-source': 'VII/118/names',
        '-out.form': 'TSV',
        '-out.max': '-1',  # No limit
        '-out': 'Object,Name',
        '-out.meta': '',
        'Object': 'M*'  # Filter for Messier objects
    }

    logger.info("Downloading Messier catalog names...")
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
    data_lines = [line for line in lines[data_start+1:] if line.strip()]

    with open("data/raw/messier_names.tsv", "w") as f:
        f.write(header + '\n')
        f.write('\n'.join(data_lines))

    return len(data_lines)

def download_ngc_data():
    url = "https://vizier.cds.unistra.fr/viz-bin/VizieR-4"
    params = {
        '-source': 'VII/118/ngc2000',
        '-out.form': 'TSV',
        '-out.max': '-1',  # No limit
        '-out': 'Name,RAJ2000,DEJ2000,Diam',
        '-out.meta': ''
    }

    logger.info("Downloading NGC data for Messier objects...")
    response = requests.get(url, params=params)
    Path("data/intermediate").mkdir(parents=True, exist_ok=True)

    lines = response.text.split('\n')
    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith('#'):
            data_start = i
            break

    if data_start >= len(lines):
        raise ValueError("No data found in VizieR response")

    with open("data/intermediate/messier_ngc_data.tsv", "w") as f:
        f.write('\n'.join(lines[data_start:]))

def process_messier_catalog():
    if not Path("data/raw/messier_names.tsv").exists():
        num_objects = download_messier_names()
        logger.info(f"Downloaded {num_objects} Messier objects")

    logger.info("Processing Messier catalog data...")
    names_df = pd.read_csv("data/raw/messier_names.tsv", sep='\t', comment='#')

    if not Path("data/intermediate/messier_ngc_data.tsv").exists():
        download_ngc_data()

    ngc_df = pd.read_csv("data/intermediate/messier_ngc_data.tsv", sep='\t', comment='#')

    processed_df = pd.DataFrame({
        'name': names_df['Object'],
        'catalog': 'Messier',
        'ra': pd.to_numeric(ngc_df['RAJ2000'], errors='coerce'),
        'dec': pd.to_numeric(ngc_df['DEJ2000'], errors='coerce'),
        'size': pd.to_numeric(ngc_df['Diam'], errors='coerce')
    })

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    processed_df.to_csv('data/processed/processed_messier.csv', index=False)
    logger.info(f"Processed {len(processed_df)} Messier objects")
    return processed_df

if __name__ == "__main__":
    process_messier_catalog()
