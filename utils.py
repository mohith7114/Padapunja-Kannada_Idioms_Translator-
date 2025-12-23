# utils.py
import logging
from extensions import db
from models import Idiom
import os
from datetime import datetime

# GLOBAL CACHE
IDIOM_CACHE = []

def refresh_idiom_cache():
    """Fetches all idioms, converts to dicts, sorts, and stores in RAM."""
    global IDIOM_CACHE
    try:
        all_idioms = Idiom.query.all()
        # Convert to list of dicts
        IDIOM_CACHE = [idiom.to_dict() for idiom in all_idioms]
        # Sort by length (longest first)
        IDIOM_CACHE.sort(key=lambda x: len(x['idiom']), reverse=True)
        logging.info(f"Cache refreshed! Loaded {len(IDIOM_CACHE)} idioms.")
    except Exception as e:
        logging.error(f"Failed to refresh cache: {e}")

def get_cached_idioms():
    global IDIOM_CACHE
    if not IDIOM_CACHE:
        refresh_idiom_cache()
    return IDIOM_CACHE


def datetimeformat(value):
    if isinstance(value, str):
        try:
            # Parse string to datetime first
            from datetime import datetime
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except:
            return value
    return value.strftime("%d-%m-%Y %I:%M:%S %p")