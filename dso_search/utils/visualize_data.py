"""
Generate visualizations of DSO catalog data composition.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def load_all_catalogs() -> pd.DataFrame:
    """Load and combine all processed catalog data."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    dfs = []

    for csv_file in data_dir.glob("processed_*.csv"):
        df = pd.read_csv(csv_file)
        catalog_name = csv_file.stem.replace('processed_', '').upper()
        df['source_catalog'] = catalog_name
        # Ensure consistent column names
        df = df.rename(columns={
            'type': 'object_type',
            'diam': 'diameter',
            'mag': 'magnitude'
        })
        dfs.append(df)

    if not dfs:
        raise ValueError(f"No processed catalog files found in {data_dir}")

    return pd.concat(dfs, ignore_index=True)

def create_visualizations():
    """Generate various visualizations of the DSO data."""
    data = load_all_catalogs()
    output_dir = Path(__file__).parent.parent.parent / "data" / "visualizations"
    output_dir.mkdir(exist_ok=True)

    # Set basic plot style
    plt.rcParams['figure.figsize'] = [12, 8]
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3

    # 1. Object Count by Catalog
    plt.figure(figsize=(15, 8))
    catalog_counts = data['source_catalog'].value_counts()
    ax = catalog_counts.plot(kind='bar')
    plt.title('Number of Objects by Catalog', fontsize=14)
    plt.xlabel('Catalog', fontsize=12)
    plt.ylabel('Number of Objects', fontsize=12)
    plt.xticks(rotation=45)
    # Add value labels on top of bars
    for i, v in enumerate(catalog_counts):
        ax.text(i, v, str(v), ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(output_dir / 'objects_by_catalog.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Sky Distribution (RA/Dec)
    plt.figure(figsize=(15, 10))
    plt.scatter(data['ra'], data['dec'], alpha=0.5, s=1, c=data['source_catalog'].astype('category').cat.codes, cmap='tab20')
    plt.title('Sky Distribution of Deep Space Objects', fontsize=14)
    plt.xlabel('Right Ascension (degrees)', fontsize=12)
    plt.ylabel('Declination (degrees)', fontsize=12)
    plt.colorbar(ticks=range(len(data['source_catalog'].unique())),
                label='Catalog',
                boundaries=range(len(data['source_catalog'].unique())+1))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'sky_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Size Distribution
    plt.figure(figsize=(15, 8))
    # Filter out null values and extreme outliers
    size_data = data[data['diameter'].notna() & (data['diameter'] < np.percentile(data['diameter'].dropna(), 99))]
    sns.boxplot(x='source_catalog', y='diameter', data=size_data)
    plt.title('Object Size Distribution by Catalog (excluding outliers)', fontsize=14)
    plt.xlabel('Catalog', fontsize=12)
    plt.ylabel('Diameter (arcminutes)', fontsize=12)
    plt.xticks(rotation=45)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(output_dir / 'size_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Data Completeness
    plt.figure(figsize=(12, 6))
    completeness = data.notna().mean() * 100
    completeness = completeness.sort_values()
    ax = completeness.plot(kind='bar')
    plt.title('Data Completeness by Field', fontsize=14)
    plt.xlabel('Field', fontsize=12)
    plt.ylabel('Completeness (%)', fontsize=12)
    plt.xticks(rotation=45)
    # Add value labels on top of bars
    for i, v in enumerate(completeness):
        ax.text(i, v, f'{v:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(output_dir / 'data_completeness.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. RA Distribution
    plt.figure(figsize=(15, 8))
    for catalog in data['source_catalog'].unique():
        catalog_data = data[data['source_catalog'] == catalog]
        plt.hist(catalog_data['ra'], bins=50, alpha=0.3, label=catalog)
    plt.title('Distribution of Objects by Right Ascension', fontsize=14)
    plt.xlabel('Right Ascension (degrees)', fontsize=12)
    plt.ylabel('Number of Objects', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(output_dir / 'ra_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    create_visualizations()
