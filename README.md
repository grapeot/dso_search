# Deep Space Object Search API

A FastAPI-based service for searching and retrieving information about deep space objects from various astronomical catalogs.

## Data Overview

Our astronomical catalog includes data from multiple sources, processed and standardized for easy access. Here are some visualizations that showcase the scope and quality of our data:

### Objects by Catalog
![Objects by Catalog](data/visualizations/objects_by_catalog.png)
*Distribution of objects across different astronomical catalogs*

### Sky Distribution
![Sky Distribution](data/visualizations/sky_distribution.png)
*Spatial distribution of objects across the celestial sphere*

### Size Distribution
![Size Distribution](data/visualizations/size_distribution.png)
*Range and distribution of object sizes within each catalog*

### Data Completeness
![Data Completeness](data/visualizations/data_completeness.png)
*Completeness of different data fields across catalogs*

### Right Ascension Distribution
![RA Distribution](data/visualizations/ra_distribution.png)
*Distribution of objects across right ascension values*

## Repository Structure
```
/dso_search
  /api        - FastAPI implementation
  /catalog    - Catalog processing modules
  /utils      - Utility functions
/tests        - Test suite
/data
  /raw           - Original catalog files
  /intermediate  - Processed intermediate files
  /processed     - Final processed catalog files
  /visualizations - Data visualizations
```

## Data Processing

The data processing pipeline:
1. Downloads raw catalog data from VizieR
2. Processes and standardizes the data format
3. Validates coordinates and measurements
4. Generates processed CSV files ready for API use

## Usage

The processed catalog files in `data/processed/` are ready to use with the API:
- `processed_messier.csv`: Processed Messier catalog
- `processed_ngc.csv`: Processed NGC catalog

Each file contains standardized columns:
- name: Object identifier
- catalog: Source catalog
- ra: Right Ascension (J2000)
- dec: Declination (J2000)
- size: Angular size in arcminutes
