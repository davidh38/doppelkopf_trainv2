#!/usr/bin/env python3
"""
State management module.
Provides functions for managing shared state between WebSocket and UI.
"""
from typing import Dict, Any
from .data_structures import create_empty_lobby, create_lobby_status

# Main data structure defined globally but only used through functions
_lobby_state = create_empty_lobby()

def get_lobby_state() -> Dict:
    """Get current lobby state."""
    return _lobby_state

def set_lobby_state(state: Dict) -> None:
    """
    Update lobby state.
    Creates new immutable state from input.
    """
    global _lobby_state
    _lobby_state = create_lobby_status(
        players=tuple(state["players"]),  # Convert to tuple for immutability
        tables=tuple(state["tables"])
    )
