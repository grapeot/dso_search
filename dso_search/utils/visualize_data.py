import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_data():
    dfs = []
    data_dir = Path('data/processed')
    for csv_file in data_dir.glob('processed_*.csv'):
        df = pd.read_csv(csv_file)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def create_visualizations(df):
    # Create visualizations directory
    Path('data/visualizations').mkdir(parents=True, exist_ok=True)

    # Set style for better-looking plots
    plt.style.use('seaborn')

    # 1. Objects by Catalog
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='catalog')
    plt.title('Distribution of Objects by Catalog', fontsize=14)
    plt.xlabel('Catalog', fontsize=12)
    plt.ylabel('Number of Objects', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/visualizations/objects_by_catalog.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Sky Distribution
    plt.figure(figsize=(12, 6))
    plt.scatter(df['ra'], df['dec'], alpha=0.5, s=20)
    plt.xlabel('Right Ascension (degrees)', fontsize=12)
    plt.ylabel('Declination (degrees)', fontsize=12)
    plt.title('Sky Distribution of Deep Space Objects', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('data/visualizations/sky_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Size Distribution
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='catalog', y='size')
    plt.title('Size Distribution by Catalog', fontsize=14)
    plt.xlabel('Catalog', fontsize=12)
    plt.ylabel('Size (arcminutes)', fontsize=12)
    plt.yscale('log')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/visualizations/size_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Data Completeness
    completeness = df.notna().mean() * 100
    plt.figure(figsize=(10, 6))
    completeness.plot(kind='bar')
    plt.title('Data Completeness by Field', fontsize=14)
    plt.ylabel('Completeness (%)', fontsize=12)
    plt.xlabel('Field', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('data/visualizations/data_completeness.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. RA Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['ra'], bins=50, edgecolor='black')
    plt.xlabel('Right Ascension (degrees)', fontsize=12)
    plt.ylabel('Number of Objects', fontsize=12)
    plt.title('Distribution of Objects by Right Ascension', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('data/visualizations/ra_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    df = load_data()
    create_visualizations(df)
