# Deep Space Object Search API

A FastAPI-based service for searching and retrieving information about deep space objects from various astronomical catalogs.

## Features
- Search objects by coordinates (RA/Dec)
- Multiple catalog support
- Standardized data format

## Repository Structure
```
/dso_search
  /api      - FastAPI implementation
  /catalog  - Catalog processing modules
  /utils    - Utility functions
/tests      - Test suite
/data
  /raw           - Original catalog files
  /intermediate  - Processed intermediate files
  /processed     - Final processed catalog files
  /visualizations - Data visualizations
```
