# lobby_table_handler.py

from typing import Tuple, List, Dict, Any, Callable, Optional, Union
import random
from .game_handler import play_table_rounds
from .data_structures import create_empty_lobby, create_player, create_table as create_table_dict

# Type aliases
PlayerType = Dict[str, str]
TableType = Dict[str, Any]
LobbyStatusType = Dict[str, Tuple]  # Changed from List to Tuple
Result = Tuple[bool, Optional[Any], Optional[str]]  # (success, value, error)

# Pure functions for state management

def create_result(success: bool, value: Any = None, error: str = None) -> Result:
    """Create result tuple."""
    return (success, value, error)

def connect_player(status: LobbyStatusType, token: str) -> Result:
    """Add player to lobby status players list."""
    if not token:
        return create_result(False, error="Token is required")
    
    new_status = {
        "players": status["players"] + (token,),  # Convert to tuple
        "tables": status["tables"]
    }
    return create_result(True, new_status)

def login_player(status: LobbyStatusType, name: str) -> Result:
    """Create new player and add to lobby."""
    if not name:
        return create_result(False, error="Player name is required")
    
    # Check if player with same name exists
    for player in status["players"]:
        if isinstance(player, dict) and player["name"] == name:
            return create_result(False, error="Player name already exists")
    
    token = f"token_{random.randint(10000, 99999)}"
    player = create_player(
        session="",
        name=name,
        type_="",
        uuid=token
    )
    new_status = {
        "players": status["players"] + (player,),  # Convert to tuple
        "tables": status["tables"]
    }
    print(f"Created player: {player}")  # Debug print
    print(f"New lobby status: {new_status}")  # Debug print
    return create_result(True, (new_status, player))

def create_table(status: LobbyStatusType, name: str, rounds: int) -> Result:
    """Create new table and add to lobby."""
    if not name:
        return create_result(False, error="Table name is required")
    if rounds <= 0:
        return create_result(False, error="Number of rounds must be positive")
    
    table = create_table_dict(
        tablename=name,
        players=tuple(),  # Empty tuple
        rounds=tuple(),   # Empty tuple
        status="open"
    )
    new_status = {
        "players": status["players"],
        "tables": status["tables"] + (table,)  # Convert to tuple
    }
    return create_result(True, (new_status, table))

def add_player_to_table(status: LobbyStatusType, table: TableType, player_name: str) -> Result:
    """Add player to table if space available."""
    if len(table["players"]) >= 4:
        return create_result(False, error="Table is full")
    
    updated_table = {
        **table,
        "players": table["players"] + (player_name,)  # Convert to tuple
    }
    
    # Convert list comprehension to tuple
    updated_tables = tuple(
        updated_table if t["tablename"] == table["tablename"] else t
        for t in status["tables"]
    )
    
    new_status = {
        "players": status["players"],
        "tables": updated_tables
    }
    
    return create_result(True, (new_status, True, updated_table))

def start_table(status: LobbyStatusType, table: TableType) -> Result:
    """Start table if requirements met."""
    if len(table["players"]) != 4:
        return create_result(False, error="Table must have exactly 4 players")
    
    updated_table = {
        **table,
        "status": "playing",
        "rounds": tuple()  # Empty tuple
    }
    
    # Convert list comprehension to tuple
    updated_tables = tuple(
        updated_table if t["tablename"] == table["tablename"] else t
        for t in status["tables"]
    )
    
    new_status = {
        "players": status["players"],
        "tables": updated_tables
    }
    
    return create_result(True, (new_status, True, updated_table))

# Public API

def handle_connect_player(state: LobbyStatusType, token: str) -> Result:
    """Connect player to lobby."""
    return connect_player(state, token)

def handle_login_player(state: LobbyStatusType, name: str) -> Result:
    """Login new player to lobby."""
    result = login_player(state, name)
    if result[0]:  # success
        new_state, player = result[1]
        return create_result(True, (new_state, player))
    return result

def handle_create_table(state: LobbyStatusType, name: str, rounds: int) -> Result:
    """Create new table in lobby."""
    result = create_table(state, name, rounds)
    if result[0]:  # success
        new_state, table = result[1]
        return create_result(True, (new_state, table))
    return result

def handle_add_player_to_table(state: LobbyStatusType, table: TableType, player_name: str) -> Result:
    """Add player to existing table."""
    result = add_player_to_table(state, table, player_name)
    if result[0]:  # success
        new_state, _, updated_table = result[1]
        return create_result(True, (new_state, updated_table))
    return result

def handle_start_table(state: LobbyStatusType, table: TableType) -> Result:
    """Start table if requirements met."""
    result = start_table(state, table)
    if result[0]:  # success
        new_state, _, updated_table = result[1]
        return create_result(True, (new_state, updated_table))
    return result
