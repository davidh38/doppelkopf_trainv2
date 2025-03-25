"""
Configuration settings for the application.
Uses immutable data structures and functional approach.
"""

from typing import Literal, Union
from functools import partial
from pathlib import Path
import json

# Valid frontend types as a tuple (immutable)
VALID_FRONTEND_TYPES = ('terminal', 'web')
FrontendType = Literal['terminal', 'web']

# Config file path relative to this file
CONFIG_PATH = Path(__file__).parent / 'config.json'

def read_config() -> dict:
    """Read config from file, return default if file doesn't exist."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {'frontend_type': 'terminal'}

def write_config(config: dict) -> None:
    """Write config to file."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get_frontend_type() -> FrontendType:
    """Get the current frontend type."""
    return read_config()['frontend_type']

def set_frontend_type(frontend_type: str) -> FrontendType:
    """
    Set the frontend type if valid.
    Returns the new frontend type if valid, raises ValueError if invalid.
    """
    if frontend_type not in VALID_FRONTEND_TYPES:
        raise ValueError(f"Frontend type must be one of {VALID_FRONTEND_TYPES}")
    
    config = read_config()
    config['frontend_type'] = frontend_type
    write_config(config)
    return frontend_type
