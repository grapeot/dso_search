# Deep Space Object Search API

A FastAPI-based backend service for searching and retrieving information about deep space objects from various astronomical catalogs.

## Data Collection

The data in this project is collected from multiple authoritative astronomical catalogs:

### Catalogs and Sources

1. **Messier Catalog**
   - Source: SIMBAD Astronomical Database
   - Collection Method: `fetch_messier_simbad.py` script queries SIMBAD API
   - Additional diameter data from NASA HEASARC

2. **NGC/IC Catalogs**
   - Source: NASA/IPAC Extragalactic Database (NED)
   - Collection Method: `process_ngc.py` processes structured data files

3. **Specialized Catalogs**
   - Abell Galaxy Clusters
   - Barnard Dark Nebulae
   - Caldwell Objects
   - LBN (Lynds Bright Nebulae)
   - LDN (Lynds Dark Nebulae)
   - Sharpless HII Regions
   - van den Bergh Reflection Nebulae

All coordinates are standardized to J2000 epoch. Object sizes are in arcminutes.

## Data Processing

The data processing pipeline consists of several steps:

1. Raw data collection from authoritative sources
2. Coordinate standardization to J2000 epoch
3. Object type normalization
4. Size and magnitude validation
5. Cross-matching between catalogs
6. Data quality analysis

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

## Data Location

Processed catalog data is stored in the `data/` directory:
- `processed_messier.csv`: Messier catalog objects
- `processed_ngc.csv`: NGC/IC catalog objects
- Additional specialized catalog files

Raw data and intermediate processing files are stored in `data/raw/`.

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
