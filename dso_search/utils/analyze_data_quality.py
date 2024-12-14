import pandas as pd
import json
from pathlib import Path

def analyze_catalog_data():
    print("Loading merged DSO data...")
    df = pd.read_csv('data/merged_dso.csv')
    
    catalogs = ['Messier', 'Barnard', 'Sharpless', 'Caldwell', 'LDN', 'NGC', 'IC', 'Abell', 'LBN', 'VdB']
    
    for catalog in catalogs:
        catalog_df = df[df['catalog'] == catalog]
        print(f"\nSample of {catalog} objects:")
        print(catalog_df.head())
        print(f"\n{catalog} Statistics:")
        print(f"Total objects: {len(catalog_df)}")
        print("Missing values:")
        print(catalog_df.isnull().sum())
        print("\nName format examples:")
        print(catalog_df['name'].head())
        print("-" * 80)

if __name__ == "__main__":
    analyze_catalog_data()
