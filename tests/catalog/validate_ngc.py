import pandas as pd
import sys
from pathlib import Path

def validate_ngc_data(file_path):
    print(f"Validating NGC data from {file_path}")

    # Read TSV file, skipping initial comments
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find where the actual data starts (after headers)
    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith('#'):
            data_start = i
            break

    # Read the data into a pandas DataFrame
    df = pd.read_csv(file_path, sep='\t', skiprows=data_start, names=['Name', 'RAB2000', 'DEB2000', 'Diam'])

    print("\nDataset Overview:")
    print(f"Total rows: {len(df)}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nColumn info:")
    print(df.info())

    print("\nMissing values:")
    print(df.isnull().sum())

    return df

if __name__ == "__main__":
    data_dir = Path("/home/ubuntu/dso-search-api/dso-search-api/data")
    ngc_file = data_dir / "ngc2000.tsv"

    if not ngc_file.exists():
        print(f"Error: {ngc_file} not found!")
        sys.exit(1)

    df = validate_ngc_data(ngc_file)
