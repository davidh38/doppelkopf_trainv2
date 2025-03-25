# src/frontend/lobby_table_output.py

from typing import Tuple, Optional, List
from src.backend.lobby_table_handler import get_lobby_status
from src.backend.data_structures import Table

def output_lobby(lobby_list: List[str]) -> None:
    """
    Outputs all players in the lobby
    Outputs all tables with the players in the table
    """
    lobby_status = get_lobby_status()
    print("Lobby:")
    print("  Players:")
    for player in lobby_list:
        print(f"    - {player}")
    print("  Tables:")
    for table in lobby_status.tables:
        print(f"    - {table.tablename} (Players: {table.players})")

def output_table(table: Table) -> None:
    """
    Outputs the table information
    """
    print("Table:")
    print(f"  - Name: {table.tablename}")
    print(f"  - Players: {table.players}")

def render_screen(lobby_list: List[str], token: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Renders the current screen and gets user input.
    
    Args:
        lobby_list: List of players in the lobby
        token: Optional current player's token
        
    Returns:
        tuple: (command, args, token) where:
            - command is the numeric choice (1-5)
            - args is any additional arguments (table name, player name)
            - token is the player's token (None if not connected)
    """
    # Clear screen (using ANSI escape codes)
    print("\033[H\033[J")
    
    # Show lobby status
    output_lobby(lobby_list)
    
    # Show current token if connected
    if token:
        print(f"\nYour token: {token}")
    
    # Show menu based on connection state
    print("\nAvailable actions:")
    if not token:
        print("  5 [name]        - Connect player (e.g., \"5 john\")")
    else:
        print("  1 [table_name]  - Create new table (e.g., \"1 mytable\")")
        print("  2 [table_name]  - Join table (e.g., \"2 mytable\")")
        print("  3 [table_name]  - Start table (e.g., \"3 mytable\")")
        print("  4               - Exit")
    
    # Get and parse input
    user_input = input("\nEnter command: ").strip()
    parts = user_input.split(maxsplit=2)  # Split into max 3 parts: command, args, token
    
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    new_token = parts[2] if len(parts) > 2 else token  # Use existing token if not provided
    
    # For connect command (5), we don't expect a token
    if command == "5":
        new_token = None
    
    return command, args, new_token
