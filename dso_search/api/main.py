"""
Main FastAPI application for the DSO Search API.
Provides endpoints for searching deep space objects by coordinates.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import List, Optional

from .models import Coordinates, DeepSpaceObject, SearchResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Deep Space Object Search API",
    description="Search for deep space objects by coordinates across multiple astronomical catalogs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_catalog_data() -> pd.DataFrame:
    """Load and combine processed catalog data."""
    try:
        dfs = []
        data_dir = Path('data/processed')
        for csv_file in data_dir.glob('processed_*.csv'):
            df = pd.read_csv(csv_file)
            dfs.append(df)
        return pd.concat(dfs, ignore_index=True)
    except Exception as e:
        logger.error(f"Error loading catalog data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load catalog data")

# Load catalog data at startup
catalog_data = load_catalog_data()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "catalog_count": len(catalog_data)}

@app.post("/search", response_model=SearchResponse)
async def search_objects(coords: Coordinates):
    """
    Search for deep space objects near the specified coordinates.

    Args:
        coords: Search coordinates and radius

    Returns:
        List of matching deep space objects
    """
    try:
        # Calculate angular distances using numpy for better performance
        ra_diff = catalog_data['ra'] - coords.ra
        dec_diff = catalog_data['dec'] - coords.dec

        # Use spherical trigonometry for accurate distances (Haversine formula)
        distances = (
            2 * np.arcsin(np.sqrt(
                np.sin(np.deg2rad(dec_diff) / 2) ** 2 +
                np.cos(np.deg2rad(coords.dec)) *
                np.cos(np.deg2rad(catalog_data['dec'])) *
                np.sin(np.deg2rad(ra_diff) / 2) ** 2
            )) * 180 / np.pi
        )

        # Filter objects within search radius
        matches = catalog_data[distances <= coords.radius]

        # Convert to response model
        objects = [
            DeepSpaceObject(
                name=row['name'],
                catalog=row['catalog'],
                ra=row['ra'],
                dec=row['dec'],
                size=row['size']
            )
            for _, row in matches.iterrows()
        ]

        return SearchResponse(objects=objects, count=len(objects))

    except Exception as e:
        logger.error(f"Error processing search request: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")

@app.get("/catalogs")
async def list_catalogs():
    """List available catalogs and their object counts."""
    try:
        counts = catalog_data['catalog'].value_counts().to_dict()
        return {
            "catalogs": counts,
            "total_objects": len(catalog_data)
        }
    except Exception as e:
        logger.error(f"Error listing catalogs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list catalogs")
