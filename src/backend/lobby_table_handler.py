# lobby_table_handler.py

from typing import Tuple, Callable, List, Dict, Any
from src.backend.data_structures import PlayerType, TableType, LobbyStatusType
from .game_handler import play_table_rounds

def create_empty_lobby() -> LobbyStatusType:
    """
    Create an empty lobby status.
    
    Returns:
        LobbyStatusType: A new empty lobby status
    """
    return {
        "players": [],
        "tables": []
    }

# Pure functions that don't use global state
# These are the core functions that implement the business logic

def connect_player_pure(status: LobbyStatusType, token: str) -> Tuple[LobbyStatusType, bool]:
    """
    Pure function version of connect_player that doesn't use global variables.
    
    Args:
        status: The current lobby status
        token: The player's token
        
    Returns:
        tuple: (new_status, success_flag)
    """
    # TODO: Implement token validation
    if token:
        return {
            "players": status["players"] + [token],
            "tables": status["tables"]
        }, True
    else:
        return status, False

def login_player_pure(status: LobbyStatusType, name: str) -> Tuple[LobbyStatusType, PlayerType]:
    """
    Pure function version of login_player that doesn't use global variables.
    
    Args:
        status: The current lobby status
        name: The player's name
        
    Returns:
        tuple: (new_status, player)
    """
    # TODO: Implement name uniqueness check
    token = generate_token()  # Implement token generation
    player = {
        "session": "",
        "name": name,
        "type": "",
        "uuid": token
    }
    new_status = {
        "players": status["players"] + [player],
        "tables": status["tables"]
    }
    return new_status, player

def create_table_pure(status: LobbyStatusType, name: str, rounds: int) -> Tuple[LobbyStatusType, TableType]:
    """
    Pure function version of create_table that doesn't use global variables.
    
    Args:
        status: The current lobby status
        name: The table name
        rounds: Number of rounds
        
    Returns:
        tuple: (new_status, table)
    """
    table = {
        "tablename": name,
        "players": [],
        "status": "open",
        "rounds": None,
        "num_rounds": rounds,
        "game_dict": ""
    }
    new_status = {
        "players": status["players"],
        "tables": status["tables"] + [table]
    }
    return new_status, table

def add_player_to_table_pure(status: LobbyStatusType, table: TableType, player_name: str) -> Tuple[LobbyStatusType, bool, TableType]:
    """
    Pure function version of add_player_to_table that doesn't use global variables.
    
    Args:
        status: The current lobby status
        table: The table object
        player_name: The player's name
        
    Returns:
        tuple: (new_status, success_flag, updated_table)
    """
    if len(table["players"]) < 4:
        updated_table = {
            **table,
            "players": table["players"] + [player_name]
        }
        
        # Find the table in the status.tables list and replace it
        updated_tables = []
        for t in status["tables"]:
            if t["tablename"] == table["tablename"]:
                updated_tables.append(updated_table)
            else:
                updated_tables.append(t)
        
        new_status = {
            "players": status["players"],
            "tables": updated_tables
        }
        
        return new_status, True, updated_table
    else:
        return status, False, table

def start_table_pure(status: LobbyStatusType, table: TableType) -> Tuple[LobbyStatusType, bool, TableType]:
    """
    Pure function version of start_table that doesn't use global variables.
    
    Args:
        status: The current lobby status
        table: The table object
        
    Returns:
        tuple: (new_status, success_flag, updated_table)
    """
    # TODO: Implement player sitting at the table check
    if len(table["players"]) == 4:
        # First set table to running state
        updated_table = {
            **table,
            "status": "running"
        }
        
        # Play all rounds for the table
        updated_table = play_table_rounds(updated_table)
        
        # Find the table in the status.tables list and replace it
        updated_tables = []
        for t in status["tables"]:
            if t["tablename"] == table["tablename"]:
                updated_tables.append(updated_table)
            else:
                updated_tables.append(t)
        
        new_status = {
            "players": status["players"],
            "tables": updated_tables
        }
        
        return new_status, True, updated_table
    else:
        return status, False, table

def generate_token() -> str:
    """
    Generate a unique token for the player
    
    Returns:
        str: A unique token
    """
    # TODO: Implement token generation logic
    return "token"  # Placeholder token

# Module-level cache for the current state
# This is not a global variable, but a closure that encapsulates the state
def create_state_cache() -> Tuple[Callable[[], LobbyStatusType], Callable[[LobbyStatusType], None]]:
    state = create_empty_lobby()
    
    def get_state() -> LobbyStatusType:
        nonlocal state
        return state
    
    def set_state(new_state: LobbyStatusType) -> None:
        nonlocal state
        state = new_state
    
    return get_state, set_state

# Create the state getters and setters
get_current_state, set_current_state = create_state_cache()

# Public API functions that use the pure functions
def connect_player(token: str) -> bool:
    """
    If token valid, add player to lobby status players list
    Else: tell the player to login
    
    Args:
        token: The player's token
        
    Returns:
        bool: True if the player was connected, False otherwise
    """
    current_state = get_current_state()
    new_state, success = connect_player_pure(current_state, token)
    set_current_state(new_state)
    return success

def login_player(name: str) -> PlayerType:
    """
    Consistency check, whether name is unique
    Create token for player
    Create dict for player
    Add player to lobby status players list
    
    Args:
        name: The player's name
        
    Returns:
        PlayerType: The created player object
    """
    current_state = get_current_state()
    new_state, player = login_player_pure(current_state, name)
    set_current_state(new_state)
    return player

def create_table(name: str, rounds: int) -> TableType:
    """
    Create table dict
    change status to open
    Add table to lobby status tables list
    
    Args:
        name: The table name
        rounds: Number of rounds
        
    Returns:
        TableType: The created table object
    """
    current_state = get_current_state()
    new_state, table = create_table_pure(current_state, name, rounds)
    set_current_state(new_state)
    return table

def add_player_to_table(table: TableType, player_name: str) -> bool:
    """
    Check for max of 4 players
    Else: add player to table and update the table in lobby status
    
    Args:
        table: The table object
        player_name: The player's name
        
    Returns:
        bool: True if the player was added, False otherwise
    """
    current_state = get_current_state()
    new_state, success, _ = add_player_to_table_pure(current_state, table, player_name)
    set_current_state(new_state)
    return success

def start_table(table: TableType) -> bool:
    """
    Check if player is sitting at the table
    Consistency check: are four players at the table
    Change mode to running mode
    Assign a game_dict to the table
    Call init_game function -> todo
    
    Args:
        table: The table object
        
    Returns:
        bool: True if the table was started, False otherwise
    """
    current_state = get_current_state()
    new_state, success, _ = start_table_pure(current_state, table)
    set_current_state(new_state)
    return success

def get_lobby_status() -> LobbyStatusType:
    """
    Return the current lobby status
    
    Returns:
        LobbyStatusType: The current lobby status
    """
    return get_current_state()

def reset_lobby_status() -> LobbyStatusType:
    """
    Reset the lobby status for testing purposes.
    
    Returns:
        LobbyStatusType: A new empty lobby status
    """
    new_state = create_empty_lobby()
    set_current_state(new_state)
    return new_state
