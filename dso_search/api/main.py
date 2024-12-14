from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

app = FastAPI(
    title="Deep Space Object Search API",
    description="API for searching astronomical objects within a given field of view",
    version="1.0.0"
)

def load_dso_data() -> pd.DataFrame:
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    dso_data = []
    for csv_file in data_dir.glob("processed_*.csv"):
        try:
            df = pd.read_csv(csv_file)
            dso_data.append(df)
        except Exception as e:
            print(f"Error loading {csv_file}: {str(e)}")
            continue

    if not dso_data:
        return pd.DataFrame()
    return pd.concat(dso_data, ignore_index=True)

try:
    DSO_DATA = load_dso_data()
except Exception as e:
    print(f"Error loading DSO data: {str(e)}")
    DSO_DATA = pd.DataFrame()

def is_within_fov(ra: float, dec: float, center_ra: float, center_dec: float,
                 fov_width: float, fov_height: float) -> bool:
    ra1, dec1 = np.radians([ra, dec])
    ra2, dec2 = np.radians([center_ra, center_dec])

    delta_ra = ra1 - ra2
    delta_dec = dec1 - dec2

    a = np.sin(delta_dec/2)**2 + np.cos(dec1) * np.cos(dec2) * np.sin(delta_ra/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    separation_deg = np.degrees(c)

    ra_distance = abs(ra - center_ra) * np.cos(np.radians(dec))
    dec_distance = abs(dec - center_dec)

    return ra_distance <= fov_width/2 and dec_distance <= fov_height/2

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/search")
async def search_dsos(
    center_ra: float = Query(..., description="Center Right Ascension in degrees", ge=0, lt=360),
    center_dec: float = Query(..., description="Center Declination in degrees", ge=-90, le=90),
    fov_width: float = Query(..., description="Field of View width in degrees", gt=0, le=180),
    fov_height: float = Query(..., description="Field of View height in degrees", gt=0, le=180)
) -> Dict[str, Any]:
    if DSO_DATA.empty:
        raise HTTPException(status_code=503, detail="DSO data not available")

    mask = DSO_DATA.apply(
        lambda row: is_within_fov(
            row['ra'], row['dec'],
            center_ra, center_dec,
            fov_width, fov_height
        ),
        axis=1
    )

    results = DSO_DATA[mask].replace({np.nan: None}).to_dict('records')

    valid_results = [
        obj for obj in results
        if all(key in obj and obj[key] is not None
              for key in ['name', 'ra', 'dec', 'diameter'])
    ]

    return {
        "objects": valid_results,
        "total": len(valid_results)
    }
