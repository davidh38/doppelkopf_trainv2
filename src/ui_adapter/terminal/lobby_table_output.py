# src/ui-adapter/terminal/lobby_table_output.py

from typing import Tuple, Optional, List, NoReturn, Dict, Any
from services.lobby_table_handler import create_table, add_player_to_table, start_table, create_empty_lobby
from services.data_structures import TableType, PlayerType
from .game_output import run_game_interface
import asyncio

import logging
logger = logging.getLogger('client.ui')

# Local state management
_current_lobby = create_empty_lobby()

def get_lobby_state() -> Dict:
    """Get current lobby state."""
    return _current_lobby

def set_lobby_state(state: Dict) -> None:
    """Update lobby state."""
    global _current_lobby
    _current_lobby = state.copy()  # Make a copy to ensure state isolation

async def run_terminal_ui_adapter(websocket_client: Any) -> NoReturn:
    """
    Public API: Run the terminal UI adapter.
    This is the only public function that should be called from outside.
    """
    token = None
    while True:
        # Get current state and render screen
        lobby_status = get_lobby_state()
        command, args, token = _render_screen(lobby_status["players"], token)
        
        # Handle command
        should_exit, token = await _handle_command(command, args, token, lobby_status, websocket_client)
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
        print("  4                       - Exit")
        print("  6                       - Refresh lobby status")

def _get_user_input(token: Optional[str]) -> Tuple[str, str, Optional[str]]:
    """Get and parse user input"""
    user_input = input("\nEnter command: ").strip().lower()
    parts = user_input.split()
    
    command = parts[0]
    args = " ".join(parts[1:]) if len(parts) > 1 else ""
    
    # Keep the token unless explicitly logging out
    return command, args, token

def _output_lobby(lobby_list: List[PlayerType]) -> None:
    """
    Output all players in the lobby and tables with their players
    """
    lobby_status = get_lobby_state()
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

async def _handle_command(command: str, args: str, token: Optional[str], lobby_status: Dict, websocket_client: Any) -> Tuple[bool, Optional[str]]:
    """
    Handle a single command and return whether to exit and the new token state.
    
    Args:
        command: The command to execute (1-5)
        args: Additional arguments for the command
        token: Current player token
        lobby_status: Current lobby state
        websocket_client: WebSocket client instance
        
    Returns:
        tuple: (should_exit, new_token)
    """
    try:
        if command == "5":  # Connect player
            if not args:
                print("\nError: Player name required")
                print("Usage: 5 <name>")
                print("Example: 5 john")
            else:
                # Find player in lobby state
                for player in lobby_status["players"]:
                    if isinstance(player, dict) and player["name"] == args:
                        print("\nError: Player name already exists")
                        input("Press Enter to continue...")
                        return False, token
                
                from socket_adapter.client_adapter import send_message
                await send_message(websocket_client, 'player_connect', {'name': args, 'type': 'player'})
                print("\nConnecting...")
                # Wait a moment for the connection response and lobby update
                await asyncio.sleep(0.5)
            return False, token
        
        elif command == "1" and token:  # Create table
            parts = args.split()
            try:
                if len(parts) < 2:
                    print("\nError: Both table name and number of rounds are required")
                    print("Usage: 1 <table_name> <rounds>")
                    print("Example: 1 mytable 3")
                else:
                    table_name = parts[0]
                    rounds = int(parts[1])
                    if rounds <= 0:
                        print("\nError: Number of rounds must be positive")
                    else:
                        current_state = get_lobby_state()
                        result = create_table(current_state, table_name, rounds)
                        if result[0]:  # success
                            new_state, table = result[1]
                            print(f"\nCreated table: {table['tablename']} with {rounds} rounds")
                        else:
                            print(f"\nError: {result[2]}")  # error message
            except ValueError:
                print("\nError: Number of rounds must be a valid positive number")
                print("Example: 1 mytable 3")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "2" and token:  # Join table
            if not args:
                print("\nError: Table name required")
            else:
                table = next((t for t in lobby_status["tables"] if t["tablename"].lower() == args.lower()), None)
                if table:
                    current_state = get_lobby_state()
                    result = add_player_to_table(current_state, table, token)
                    if result[0]:  # success
                        print(f"\nJoined table: {table['tablename']}")
                    else:
                        print(f"\nError: {result[2]}")  # error message
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
                    current_state = get_lobby_state()
                    result = start_table(current_state, table)
                    if result[0]:  # success
                        new_state, _, updated_table = result[1]
                        print(f"\nStarted table: {updated_table['tablename']}")
                        run_game_interface(updated_table, token)
                    else:
                        print(f"\nError: {result[2]}")  # error message
                else:
                    print(f"\nError: Table '{args}' not found")
            input("Press Enter to continue...")
            return False, token
        
        elif command == "4":  # Exit
            print("\nGoodbye!")
            return True, token
            
        elif command == "6" and token:  # Refresh lobby status
            from socket_adapter.client_adapter import send_message
            await send_message(websocket_client, 'get_lobby_status', {})
            print("\nRefreshing lobby status...")
            input("Press Enter to continue...")
            return False, token
        
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
