"""
Models for the DSO Search API.
Defines Pydantic models for request/response validation and documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class Coordinates(BaseModel):
    """Coordinates for searching deep space objects."""
    ra: float = Field(..., ge=0, lt=360, description="Right Ascension in degrees (J2000)")
    dec: float = Field(..., ge=-90, le=90, description="Declination in degrees (J2000)")
    radius: Optional[float] = Field(1.0, gt=0, le=180, description="Search radius in degrees")


class DeepSpaceObject(BaseModel):
    """Deep space object information."""
    name: str = Field(..., description="Object designation (e.g., M31, NGC 7000)")
    catalog: str = Field(..., description="Source catalog (e.g., Messier, NGC)")
    ra: float = Field(..., description="Right Ascension in degrees (J2000)")
    dec: float = Field(..., description="Declination in degrees (J2000)")
    size: Optional[float] = Field(None, description="Object size in arcminutes")


class SearchResponse(BaseModel):
    """Response model for object searches."""
    objects: List[DeepSpaceObject] = Field(..., description="List of matching deep space objects")
    count: int = Field(..., description="Total number of objects found")
