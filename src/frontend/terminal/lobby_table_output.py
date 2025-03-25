# src/frontend/lobby_table_output.py

from typing import Tuple, Optional, List, NoReturn
from src.backend.lobby_table_handler import get_lobby_status, login_player, create_table, add_player_to_table, start_table
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

def run_terminal_frontend() -> NoReturn:
    """Run the terminal frontend."""
    print("Terminal frontend selected")
    
    token = None
    while True:
        lobby_status = get_lobby_status()
        command, args, token = render_screen(lobby_status.players, token)
        
        try:
            if command == "5":  # Connect player
                player = login_player(args)
                token = player.uuid
                print(f"\nConnected! Your token is: {token}")
                input("Press Enter to continue...")
            
            elif command == "1" and token:  # Create table
                if not args:
                    print("\nError: Table name required")
                else:
                    table = create_table(args, 10)  # Default 10 rounds
                    print(f"\nCreated table: {table.tablename}")
                input("Press Enter to continue...")
            
            elif command == "2" and token:  # Join table
                if not args:
                    print("\nError: Table name required")
                else:
                    # Find table by name
                    table = next((t for t in lobby_status.tables if t.tablename == args), None)
                    if table:
                        success = add_player_to_table(table, token)
                        if success:
                            print(f"\nJoined table: {args}")
                        else:
                            print("\nError: Could not join table")
                    else:
                        print(f"\nError: Table '{args}' not found")
                input("Press Enter to continue...")
            
            elif command == "3" and token:  # Start table
                if not args:
                    print("\nError: Table name required")
                else:
                    # Find table by name
                    table = next((t for t in lobby_status.tables if t.tablename == args), None)
                    if table:
                        success = start_table(table)
                        if success:
                            print(f"\nStarted table: {args}")
                        else:
                            print("\nError: Could not start table")
                    else:
                        print(f"\nError: Table '{args}' not found")
                input("Press Enter to continue...")
            
            elif command == "4":  # Exit
                print("\nGoodbye!")
                break
            
            else:
                if not token and command != "5":
                    print("\nError: Please connect first (option 5)")
                else:
                    print("\nError: Invalid command")
                input("Press Enter to continue...")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            input("Press Enter to continue...")
