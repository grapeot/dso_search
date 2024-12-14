import pandas as pd
import numpy as np
from pathlib import Path

def process_abell_data(north_file, south_file, output_file):
    """Process Abell catalog data into standardized format"""
    print(f"Processing Abell data from {north_file} and {south_file}")

    # Function to read and process a single file
    def read_abell_file(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Find where the actual data starts (after headers and separator)
        data_start = 0
        for i, line in enumerate(lines):
            if line.strip() and all(c in '-' for c in line.strip()):
                data_start = i + 1
                break

        # Process data lines manually due to inconsistent format
        data = []
        for line in lines[data_start:]:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) >= 5:  # Ensure we have all required fields
                    aco, ra, dec, count, rich = parts[:5]
                    data.append({
                        'ACO': aco.strip(),
                        'RA': ra.strip(),
                        'DEC': dec.strip(),
                        'Count': count.strip(),
                        'Rich': rich.strip()
                    })

        return pd.DataFrame(data)

    # Read both files
    df_north = read_abell_file(north_file)
    df_south = read_abell_file(south_file)

    # Combine the data
    df = pd.concat([df_north, df_south], ignore_index=True)

    # Clean up the data
    df = df.replace('', np.nan)  # Replace empty strings with NaN
    df = df.dropna(subset=['ACO', 'RA', 'DEC'])  # Remove rows with missing essential data

    # Convert coordinates from HH MM.M format to degrees
    def convert_ra(ra_str):
        try:
            if pd.isna(ra_str):
                return None
            parts = ra_str.split()
            if len(parts) != 2:
                return None
            hours = float(parts[0])
            minutes = float(parts[1])
            return (hours + minutes/60) * 15  # Convert to degrees (15 degrees per hour)
        except:
            return None

    def convert_dec(dec_str):
        try:
            if pd.isna(dec_str):
                return None
            parts = dec_str.split()
            if len(parts) != 2:
                return None
            degrees = float(parts[0])
            minutes = float(parts[1])
            return degrees + minutes/60 * (1 if degrees >= 0 else -1)
        except:
            return None

    # Create standardized format
    result_df = pd.DataFrame({
        'name': df['ACO'].apply(lambda x: f"Abell{str(x).strip().zfill(4)}" if pd.notna(x) else None),
        'catalog': 'Abell',
        'ra': df['RA'].apply(convert_ra),
        'dec': df['DEC'].apply(convert_dec),
        'diameter': None  # Abell clusters don't have standard diameter measurements
    })

    # Remove any rows with missing essential data or invalid coordinates
    result_df = result_df.dropna(subset=['name', 'ra', 'dec'])

    # Save processed data
    result_df.to_csv(output_file, index=False)

    print("\nData Processing Summary:")
    print(f"Total objects: {len(result_df)}")
    print("\nSample of processed data:")
    print(result_df.head())
    print("\nMissing values:")
    print(result_df.isnull().sum())

    return result_df

if __name__ == "__main__":
    data_dir = Path("/home/ubuntu/dso-search-api/dso-search-api/data")
    north_file = data_dir / "abell_north.tsv"
    south_file = data_dir / "abell_south.tsv"
    output_file = data_dir / "processed_abell.csv"

    if not north_file.exists() or not south_file.exists():
        print(f"Error: Input files not found!")
        exit(1)

    df = process_abell_data(north_file, south_file, output_file)
