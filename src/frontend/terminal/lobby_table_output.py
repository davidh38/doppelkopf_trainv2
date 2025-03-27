# src/frontend/terminal/lobby_table_output.py

from typing import Tuple, Optional, List, NoReturn, Dict, Any
from src.backend.lobby_table_handler import get_lobby_status, login_player, create_table, add_player_to_table, start_table
from src.backend.data_structures import TableType, PlayerType
from .game_output import run_game_interface

def run_terminal_frontend() -> NoReturn:
    """
    Public API: Run the terminal frontend.
    This is the only public function that should be called from outside.
    """
    print("Terminal frontend selected")
    
    token = None
    while True:
        lobby_status = get_lobby_status()
        command, args, token = _render_screen(lobby_status["players"], token)
        should_exit, token = _handle_command(command, args, token, lobby_status)
        if should_exit:
            break

# Private Implementation

def _format_player(player: PlayerType) -> str:
    """Format player info for display"""
    return player["name"]

def _clear_screen() -> None:
    """Clear the terminal screen using ANSI escape codes"""
    print("\033[H\033[J")

def _display_menu(token: Optional[str]) -> None:
    """Display the appropriate menu based on connection state"""
    print("\nAvailable actions:")
    if not token:
        print("  5 [name]                - Connect player (e.g., \"5 john\")")
    else:
        print("  1 [table_name] [rounds] - Create new table (e.g., \"1 mytable 3\")")
        print("  2 [table_name]          - Join table (e.g., \"2 mytable\")")
        print("  3 [table_name]          - Start table (e.g., \"3 mytable\")")
        print("  4               - Exit")

def _get_user_input(token: Optional[str]) -> Tuple[str, str, Optional[str]]:
    """Get and parse user input"""
    user_input = input("\nEnter command: ").strip().lower()
    parts = user_input.split(maxsplit=2)
    
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    new_token = parts[2] if len(parts) > 2 else token
    
    if command == "5":
        new_token = None
    
    return command, args, new_token

def _output_lobby(lobby_list: List[PlayerType]) -> None:
    """
    Output all players in the lobby and tables with their players
    """
    lobby_status = get_lobby_status()
    print("Lobby:")
    print("  Players:")
    for player in lobby_list:
        if isinstance(player, dict):
            print(f"    - {_format_player(player)}")
        else:
            print(f"    - {player}")
    print("  Tables:")
    for table in lobby_status["tables"]:
        player_names = []
        for player_token in table["players"]:
            player = next((p for p in lobby_list if isinstance(p, dict) and p["uuid"] == player_token), None)
            if player:
                player_names.append(_format_player(player))
            else:
                player_names.append(player_token)
        print(f"    - {table['tablename']} (Players: {', '.join(player_names) if player_names else 'None'})")

def _output_table(table: TableType) -> None:
    """Output table information"""
    print("Table:")
    print(f"  - Name: {table['tablename']}")
    print(f"  - Players: {', '.join(table['players']) if table['players'] else 'None'}")

def _render_screen(lobby_list: List[PlayerType], token: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Render the current screen and get user input.
    
    Args:
        lobby_list: List of players in the lobby
        token: Optional current player's token
        
    Returns:
        tuple: (command, args, token) where:
            - command is the numeric choice (1-5)
            - args is any additional arguments (table name, player name)
            - token is the player's token (None if not connected)
    """
    _clear_screen()
    _output_lobby(lobby_list)
    
    if token:
        player = next((p for p in lobby_list if isinstance(p, dict) and p["uuid"] == token), None)
        if player:
            print(f"\nConnected as: {_format_player(player)}")
    
    _display_menu(token)
    return _get_user_input(token)

def _handle_command(command: str, args: str, token: Optional[str], lobby_status: Dict) -> Tuple[bool, Optional[str]]:
    """
    Handle a single command and return whether to exit and the new token state.
    
    Args:
        command: The command to execute (1-5)
        args: Additional arguments for the command
        token: Current player token
        lobby_status: Current lobby state
        
    Returns:
        tuple: (should_exit, new_token)
    """
    try:
        if command == "5":  # Connect player
            player = login_player(args)
            token = player["uuid"]
            print(f"\nConnected as: {_format_player(player)}")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "1" and token:  # Create table
            parts = args.split()
            if len(parts) < 2:
                print("\nError: Table name and number of rounds required (e.g., \"1 mytable 3\")")
            else:
                try:
                    table_name = parts[0]
                    rounds = int(parts[1])
                    table = create_table(table_name, rounds)
                    print(f"\nCreated table: {table['tablename']} with {rounds} rounds")
                except ValueError:
                    print("\nError: Number of rounds must be a valid number")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "2" and token:  # Join table
            if not args:
                print("\nError: Table name required")
            else:
                table = next((t for t in lobby_status["tables"] if t["tablename"].lower() == args.lower()), None)
                if table:
                    success = add_player_to_table(table, token)
                    if success:
                        print(f"\nJoined table: {table['tablename']}")
                    else:
                        print("\nError: Could not join table")
                else:
                    print(f"\nError: Table '{args}' not found")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "3" and token:  # Start table
            if not args:
                print("\nError: Table name required")
            else:
                table = next((t for t in lobby_status["tables"] if t["tablename"].lower() == args.lower()), None)
                if table:
                    success = start_table(table)
                    if success:
                        print(f"\nStarted table: {table['tablename']}")
                        run_game_interface(table, token)
                    else:
                        print("\nError: Could not start table")
                else:
                    print(f"\nError: Table '{args}' not found")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "4":  # Exit
            print("\nGoodbye!")
            return True, token
        
        else:
            if not token and command != "5":
                print("\nError: Please connect first (option 5)")
            else:
                print("\nError: Invalid command")
            input("Press Enter to continue...")
            return False, token
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        input("Press Enter to continue...")
        return False, token
