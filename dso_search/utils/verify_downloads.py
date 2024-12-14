"""Utility script to verify catalog data downloads."""
import requests
from pathlib import Path

def verify_messier_download():
    """Verify the Messier catalog download and content."""
    url = "https://raw.githubusercontent.com/OpenAstronomyData/MessierCatalog/main/messier_catalog_info.txt"
    print(f"Downloading from: {url}")
    
    response = requests.get(url)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        print("\nFirst few lines of content:")
        print("=" * 50)
        print(content[:500])
        print("=" * 50)
        
        # Save the content for inspection
        data_dir = Path("data/raw")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = data_dir / "messier_catalog_info.txt"
        with open(output_file, "w") as f:
            f.write(content)
        print(f"\nSaved content to: {output_file}")
        
        # Basic content validation
        lines = content.split("\n")
        print(f"\nTotal lines: {len(lines)}")
        if len(lines) > 2:
            print("Header lines:")
            for i in range(min(3, len(lines))):
                print(f"Line {i}: {lines[i]}")
    else:
        print(f"Failed to download: {response.status_code}")

if __name__ == "__main__":
    verify_messier_download()
