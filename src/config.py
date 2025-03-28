"""
Configuration settings for the application.
Uses immutable data structures and functional approach.
"""

from typing import Literal, Union, Dict, Any
from functools import partial
from pathlib import Path
import json

# Config file path relative to this file
CONFIG_PATH = Path(__file__).parent / 'config.json'

def read_config() -> dict:
    """Read config from file, return default if file doesn't exist."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'server': {
                'game_port': 8001,
                'lobby_port': 8002,
                'host': 'localhost'
            },
            'client': {
                'server_host': 'localhost',
                'game_port': 8001,
                'lobby_port': 8002
            }
        }

def write_config(config: dict) -> None:
    """Write config to file."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get_server_config() -> Dict[str, Any]:
    """Get server configuration."""
    return read_config()['server']

def get_client_config() -> Dict[str, Any]:
    """Get client configuration."""
    return read_config()['client']

def update_server_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update server configuration."""
    config = read_config()
    config['server'].update(updates)
    write_config(config)
    return config['server']

def update_client_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration."""
    config = read_config()
    config['client'].update(updates)
    write_config(config)
    return config['client']
