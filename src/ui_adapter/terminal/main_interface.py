#!/usr/bin/env python3

"""
IMPORTANT: DO NOT USE CLASSES IN THIS CODEBASE!

This project follows functional programming principles:
1. Use pure functions instead of classes
2. Keep data structures immutable
3. Avoid state management
4. Separate core logic from I/O

Python does not require classes, so we use functional programming patterns.
Any implementation should use standalone functions, not classes.
"""

from typing import Dict, List, Tuple, Optional, NoReturn
from .lobby_table_output import run_terminal_frontend
from .game_output import run_game_interface
from services.data_structures import TableType, PlayerType
from services.lobby_table_handler import get_lobby_status

def handle_setup() -> None:
    """
    Handle initial game setup including:
    - Display welcome message
    - Initialize necessary components
    - Set up error handlers
    """
    pass  # Implementation pending

def process_game_loop() -> bool:
    """
    Main game loop that:
    - Manages state between lobby and game
    - Handles user input and navigation
    - Coordinates between different interface components
    
    Returns:
        bool: True if the game should exit, False to continue
    """
    pass  # Implementation pending

def handle_cleanup() -> None:
    """
    Cleanup operations including:
    - Save any necessary state
    - Close connections
    - Display exit message
    """
    pass  # Implementation pending

def run_terminal_interface() -> NoReturn:
    """
    Public API: Main entry point for running the terminal interface.
    Coordinates the overall flow between different game phases.
    """
    handle_setup()
    while not process_game_loop():
        pass
    handle_cleanup()
