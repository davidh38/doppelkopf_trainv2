# src/frontend/lobby_table_output.py

from typing import Tuple
from src.backend.lobby_table_handler import table_list

def output_lobby(lobby_list):
    """
    Outputs all players in the lobby
    Outputs all tables with the players in the table
    """
    print("Lobby:")
    print("  Players:")
    for player in lobby_list:
        print(f"    - {player}")
    print("  Tables:")
    for table in table_list:
        print(f"    - {table['tablename']} (Players: {table['players']})")

def output_table(table):
    """
    Outputs the table information
    """
    print("Table:")
    print(f"  - Name: {table['tablename']}")
    print(f"  - Players: {table['players']}")

def render_screen(lobby_list) -> Tuple[str, str]:
    """
    Renders the current screen and gets user input.
    
    Args:
        lobby_list: List of players in the lobby
        
    Returns:
        tuple: (command, args) where:
            - command is the numeric choice (1-5)
            - args is any additional arguments (table name, player name)
    """
    # Clear screen (using ANSI escape codes)
    print("\033[H\033[J")
    
    # Show lobby status
    output_lobby(lobby_list)
    
    # Show menu
    print("\nAvailable actions:")
    print("  1 [table_name]  - Create new table (e.g., \"1 mytable\")")
    print("  2               - Join table")
    print("  3               - Start table")
    print("  4               - Exit")
    print("  5 [name]        - Connect player (e.g., \"5 john\")")
    
    # Get and parse input
    user_input = input("\nEnter command: ").strip()
    parts = user_input.split(maxsplit=1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args
