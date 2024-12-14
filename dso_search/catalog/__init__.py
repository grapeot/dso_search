"""
Deep Space Object catalog processing module.

This module provides functionality for processing various astronomical catalogs
including Messier, NGC, IC, and other specialized catalogs.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np

def convert_to_j2000(ra: float, dec: float, epoch: str = "J2000") -> tuple[float, float]:
    """
    Convert coordinates to J2000 epoch if needed.
    Currently assumes input is already J2000 - implement conversion if needed.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        epoch: Source epoch of coordinates

    Returns:
        tuple[float, float]: (RA, Dec) in J2000 epoch
    """
    # TODO: Implement actual epoch conversion if needed
    return (ra, dec)

def parse_coordinates(ra_str: str, dec_str: str) -> tuple[float, float]:
    """
    Parse coordinate strings in various formats to decimal degrees.

    Args:
        ra_str: Right Ascension string (HH:MM:SS or decimal degrees)
        dec_str: Declination string (DD:MM:SS or decimal degrees)

    Returns:
        tuple[float, float]: (RA, Dec) in decimal degrees

    Raises:
        ValueError: If coordinate format is invalid
    """
    try:
        # Try parsing as decimal degrees first
        ra = float(ra_str)
        dec = float(dec_str)
        return (ra, dec)
    except ValueError:
        # Try parsing as HH:MM:SS format
        try:
            ra_parts = ra_str.replace('h', ':').replace('m', ':').replace('s', '').split(':')
            dec_parts = dec_str.replace('d', ':').replace('m', ':').replace('s', '').split(':')

            ra = (float(ra_parts[0]) + float(ra_parts[1])/60 + float(ra_parts[2])/3600) * 15
            dec_sign = -1 if dec_str.startswith('-') else 1
            dec = dec_sign * (abs(float(dec_parts[0])) + float(dec_parts[1])/60 + float(dec_parts[2])/3600)

            return (ra, dec)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid coordinate format: {ra_str}, {dec_str}") from e

def normalize_object_type(obj_type: str) -> str:
    """
    Normalize object type strings to standard categories.

    Args:
        obj_type: Raw object type string from catalog

    Returns:
        str: Normalized object type
    """
    obj_type = obj_type.lower().strip()

    if any(x in obj_type for x in ['gx', 'galaxy']):
        return 'galaxy'
    elif any(x in obj_type for x in ['nebula', 'neb']):
        return 'nebula' if 'planetary' not in obj_type else 'planetary_nebula'
    elif any(x in obj_type for x in ['cluster', 'cl']):
        return 'cluster'
    else:
        return 'unknown'

def validate_coordinates(ra: float, dec: float) -> bool:
    """
    Validate that coordinates are within valid ranges.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees

    Returns:
        bool: True if coordinates are valid
    """
    return 0 <= ra < 360 and -90 <= dec <= 90
