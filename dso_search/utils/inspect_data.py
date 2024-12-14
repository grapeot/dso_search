"""Utility script to inspect catalog data formats."""
import sys
from pathlib import Path
import requests
sys.path.append(str(Path(__file__).parent.parent.parent))

def inspect_vizier_response(catalog_name, params):
    url = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv"
    print(f"\nFetching {catalog_name} data from VizieR...")
    response = requests.get(url, params=params)

    print("\nRaw Response Content:")
    print("=" * 50)
    print(response.text[:1000])  # First 1000 chars
    print("=" * 50)

    lines = response.text.split('\n')
    print(f"\nTotal lines: {len(lines)}")

    print("\nFirst 5 non-comment lines:")
    non_comment_lines = [line for line in lines if line.strip() and not line.startswith('#')][:5]
    for i, line in enumerate(non_comment_lines, 1):
        print(f"Line {i}: {line}")

    return response.text

def inspect_messier():
    params = {
        '-source': 'VII/1B/messier',
        '-out': 'Messier,RAJ2000,DEJ2000,Diam',
        '-max': '200',
        '-mime': 'csv'
    }
    return inspect_vizier_response("Messier", params)

def inspect_ngc():
    params = {
        '-source': 'VII/118/ngc2000',
        '-out': 'NGC,RAJ2000,DEJ2000,Diam',
        '-max': '8000',
        '-mime': 'csv'
    }
    return inspect_vizier_response("NGC", params)

if __name__ == "__main__":
    inspect_messier()
    inspect_ngc()
