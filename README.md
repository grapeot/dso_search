# Deep Space Object Search API

A FastAPI-based backend service for searching and retrieving information about deep space objects from various astronomical catalogs.

## Data Quality and Analysis

Our comprehensive analysis of astronomical catalogs reveals the depth and quality of our dataset:

### Catalog Distribution
![Objects by Catalog](https://files.devinusercontent.com/attachments/2c67173e-475d-4293-a005-47899b638b31/objects_by_catalog.png)

The visualization shows the distribution of objects across different catalogs, with NGC (~7,840 objects) and IC (~5,386 objects) forming the backbone of our dataset, complemented by specialized catalogs containing ~100 to ~4,000 objects each.

### Sky Coverage
![Sky Distribution](https://files.devinusercontent.com/attachments/814068da-a887-4f6b-bc94-f4fa91644d53/sky_distribution.png)

This plot demonstrates the spatial distribution of objects across the celestial sphere, revealing comprehensive coverage with notable concentrations along the galactic plane and varying density patterns between different catalogs.

### Object Size Distribution
![Size Distribution](https://files.devinusercontent.com/attachments/7ef20573-a31d-49dd-95d4-35934d52b149/size_distribution.png)

The size distribution analysis shows object sizes ranging from 0.1 to 800 arcminutes, with distinct patterns for different object types:
- Galaxy clusters: typically 2-10 arcminutes
- Nebulae: highly variable, from 1 to 500+ arcminutes
- Dark nebulae: generally larger, 10-100 arcminutes

### Data Completeness
![Data Completeness](https://files.devinusercontent.com/attachments/5937fd80-c02d-47f7-a3af-a97aa8caa373/data_completeness.png)

This visualization illustrates field completeness across catalogs:
- Coordinates: 100% complete, standardized to J2000 epoch
- Size measurements: Complete for Barnard, LBN, Sharpless, VdB; Partial for NGC/IC (~42%)
- Object types: Standardized across all catalogs

### Right Ascension Distribution
![RA Distribution](https://files.devinusercontent.com/attachments/ef5b7347-d3b3-4980-a466-5327e64f7e91/ra_distribution.png)

The Right Ascension distribution demonstrates uniform coverage around the celestial sphere, with some expected density variations in well-studied regions.

## Data Organization and Collection

The project data is organized into three main directories, each serving a specific purpose in the data processing pipeline:

### Processed Data (Direct Deliverables)
Located in `data/processed/`, these files are the final, production-ready outputs:
```
processed/
├── processed_abell.csv    # Processed Abell Galaxy Clusters
├── processed_barnard.csv  # Processed Barnard Dark Nebulae
├── processed_caldwell.csv # Processed Caldwell Objects
├── processed_ic.csv       # Processed Index Catalog
├── processed_lbn.csv      # Processed Lynds Bright Nebulae
├── processed_ldn.csv      # Processed Lynds Dark Nebulae
├── processed_messier.csv  # Processed Messier Objects
├── processed_ngc.csv      # Processed New General Catalog
├── processed_sharpless.csv# Processed Sharpless HII Regions
└── processed_vdb.csv      # Processed van den Bergh Objects
```
All processed files follow a standardized CSV format with fields:
- name: Standardized object identifier
- catalog: Source catalog identifier
- ra: Right Ascension (J2000, degrees)
- dec: Declination (J2000, degrees)
- diameter: Object size (arcminutes)

### Intermediate Processing Data
Located in `data/intermediate/`, these files represent intermediate processing stages:
```
intermediate/
├── ngc2000.tsv    # NGC/IC data after initial parsing
├── messier.tsv    # Messier data after coordinate conversion
└── *.tsv          # Other intermediate processing files
```

### Raw Source Data
Located in `data/raw/`, these files contain the original catalog data:
```
raw/
├── messier_catalog_info.txt  # Raw Messier catalog from VizieR
├── ngc2000.dat.gz           # NGC 2000.0 catalog data
└── *.dat                    # Other raw catalog files
```

## Data Collection and Processing

### How to Reproduce the Data Collection

1. Collect Raw Data:
```bash
# Download Messier catalog data
python -m dso_search.catalog.fetch_messier_simbad

# Download NGC data (automated)
python -m dso_search.catalog.fetch_ngc_data
```

2. Process Catalogs:
```bash
# Process main catalogs
python -m dso_search.catalog.process_messier
python -m dso_search.catalog.process_ngc

# Process specialized catalogs
python -m dso_search.catalog.process_abell
python -m dso_search.catalog.process_barnard
# ... other catalog processors
```

3. Verify Data:
```bash
# Run data quality checks
python -m dso_search.utils.analyze_data_quality

# Verify catalog completeness
python -m dso_search.catalog.verify_all_catalogs
```

### Data Sources and Access

1. Primary Catalogs:
   - Messier: VizieR database (VII/1B/messier)
   - NGC/IC: NASA/IPAC Extragalactic Database
   - Specialized catalogs: CDS VizieR service

2. Supplementary Data:
   - Object sizes: NASA HEASARC
   - Cross-references: SIMBAD Astronomical Database

### Code Usage Instructions

1. Setup Environment:
```bash
# Install dependencies
pip install -r requirements.txt

# Set up data directories
mkdir -p data/{raw,intermediate,processed}
```

2. Run Processing Pipeline:
```bash
# Full pipeline
./run_processing_pipeline.sh

# Individual steps
python -m dso_search.catalog.process_messier
python -m dso_search.catalog.process_ngc
```

3. Access Processed Data:
- Use CSV files in `data/processed/` for application integration
- All coordinates are in J2000 epoch
- Sizes are in arcminutes

## Code Structure

```
dso_search/
├── api/           # FastAPI implementation
├── catalog/       # Catalog processing modules
└── utils/         # Shared utilities

tests/             # Test suite
└── catalog/       # Catalog-specific tests
```

## Setup and Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Process catalog data:
```bash
python -m dso_search.catalog.process_messier
python -m dso_search.catalog.process_ngc
# ... other catalog processors
```

3. Run the API:
```bash
uvicorn dso_search.api.main:app --reload
```

## API Endpoints

- `GET /search`: Search for objects within field of view
  - Parameters:
    - `center_ra`: Right Ascension in degrees (0-360)
    - `center_dec`: Declination in degrees (-90 to 90)
    - `fov_width`: Field of view width in degrees
    - `fov_height`: Field of view height in degrees

## Development

- Run tests: `pytest tests/`
- Format code: `black dso_search/`
- Type checking: `mypy dso_search/`

## Data Quality and Learnings

Our comprehensive analysis of the astronomical catalogs revealed several key insights:

### Data Composition
- Total objects across all catalogs: ~21,000
- Largest catalogs: NGC (~7,840 objects) and IC (~5,386 objects)
- Specialized catalogs range from ~100 to ~4,000 objects
- Significant overlap between Messier and NGC catalogs

### Data Quality Metrics
- Coordinate accuracy: All coordinates successfully standardized to J2000 epoch
- Size measurements:
  - Complete for: Barnard, LBN, Sharpless, VdB catalogs
  - Partial for: NGC/IC (~42% coverage)
  - Limited for: Messier, Abell catalogs
- Object type classification standardized across catalogs

### Spatial Distribution
- Sky coverage varies significantly by catalog
- Northern hemisphere bias in some catalogs (e.g., Messier)
- Dense object clusters in galactic plane
- More uniform distribution in galaxy cluster catalogs (Abell)

### Size Distribution Patterns
- Wide range of object sizes (0.1 to 800 arcminutes)
- Median size varies significantly by catalog type:
  - Galaxy clusters: typically 2-10 arcminutes
  - Nebulae: highly variable, from 1 to 500+ arcminutes
  - Dark nebulae: generally larger, 10-100 arcminutes

### Processing Challenges
1. Coordinate System Standardization
   - Successfully converted B1950 coordinates to J2000
   - Handled various input formats (decimal, sexagesimal)
   - Validated coordinate transformations

2. Size Measurements
   - Dealt with non-uniform size reporting
   - Standardized units to arcminutes
   - Handled elliptical objects (major/minor axes)

3. Cross-Catalog Matching
   - Identified objects present in multiple catalogs
   - Resolved naming conventions
   - Merged complementary data

### Recommendations
1. Data Collection
   - Prioritize size measurement completion for NGC/IC objects
   - Consider adding magnitude data where available
   - Implement automated cross-validation

2. Processing Pipeline
   - Add validation for coordinate transformations
   - Enhance size measurement extraction
   - Implement automated outlier detection

3. Future Improvements
   - Add proper motion corrections
   - Include additional catalogs (e.g., PGC, UGC)
   - Enhance cross-matching algorithms

The data quality analysis script (`utils/analyze_data_quality.py`) provides detailed metrics on these aspects.

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and type checking
4. Submit pull request
