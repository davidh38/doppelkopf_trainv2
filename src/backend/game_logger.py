# Game Logger
# This file will handle logging of game state after every turn

import json
import os
import datetime
from pathlib import Path

# Ensure logs directory exists
def ensure_logs_directory():
    """Create logs directory if it doesn't exist."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
    return logs_dir

# Log game state
def log_game_state(game_dict):
    """
    Log the current game state to a file.
    
    Args:
        game_dict: The game dictionary containing the current game state
    """
    logs_dir = ensure_logs_directory()
    
    # Generate filename with timestamp and game ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    game_id = game_dict.get("id", "unknown")
    round_num = game_dict.get("round", 0)
    turn_num = len(game_dict.get("tricks", []))
    
    filename = f"{timestamp}_game_{game_id}_round_{round_num}_turn_{turn_num}.json"
    filepath = logs_dir / filename
    
    # Write game state to file
    with open(filepath, "w") as f:
        json.dump(game_dict, f, indent=2)
    
    print(f"Game state logged to {filepath}")

# Get game log files
def get_game_logs(game_id=None):
    """
    Get list of log files, optionally filtered by game ID.
    
    Args:
        game_id: Optional game ID to filter logs
        
    Returns:
        List of log file paths
    """
    logs_dir = ensure_logs_directory()
    
    if game_id:
        return sorted(logs_dir.glob(f"*game_{game_id}*.json"))
    else:
        return sorted(logs_dir.glob("*.json"))

# Load game state from log
def load_game_state(log_file):
    """
    Load game state from a log file.
    
    Args:
        log_file: Path to the log file
        
    Returns:
        Game dictionary loaded from the log file
    """
    with open(log_file, "r") as f:
        return json.load(f)
