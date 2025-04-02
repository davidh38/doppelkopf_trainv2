# src/ui-adapter/terminal/lobby_table_output.py

from typing import Tuple, Optional, List, NoReturn, Dict, Any
from services.lobby_table_handler import create_table, add_player_to_table, start_table, create_empty_lobby
from services.data_structures import create_player, create_table, create_lobby_status
from .game_output import run_game_interface
import asyncio
import logging

logger = logging.getLogger('client.ui')

def _format_player(player: Dict[str, Any]) -> str:
    """Format player info for display"""
    if not isinstance(player, dict) or "name" not in player:
        return "Invalid player"
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
    
    if not parts:  # Handle empty input
        return "", "", token
    
    command = parts[0]
    args = " ".join(parts[1:]) if len(parts) > 1 else ""
    
    # Keep the token unless explicitly logging out
    return command, args, token

def _output_lobby(lobby_state: Dict) -> None:
    """
    Output all players in the lobby and tables with their players
    """
    print("Lobby:")
    print("  Players:")
    for player in lobby_state["players"]:
        if isinstance(player, dict) and all(k in player for k in ["name", "uuid"]):
            print(f"    - {_format_player(player)}")
        else:
            logger.warning(f"Skipping invalid player object: {player}")
    
    print("  Tables:")
    for table in lobby_state.get("tables", []):
        if not isinstance(table, dict) or "tablename" not in table or "players" not in table:
            logger.warning(f"Skipping invalid table object: {table}")
            continue
            
        player_names = []
        for player_token in table["players"]:
            player = next((p for p in lobby_state["players"] 
                         if isinstance(p, dict) and 
                         p.get("uuid") == player_token and
                         "name" in p), None)
            if player:
                player_names.append(_format_player(player))
            else:
                player_names.append(f"Unknown({player_token})")
        
        print(f"    - {table['tablename']} (Players: {', '.join(player_names) if player_names else 'None'})")

def _output_table(table: Dict[str, Any]) -> None:
    """Output table information"""
    print("Table:")
    print(f"  - Name: {table['tablename']}")
    print(f"  - Players: {', '.join(table['players']) if table['players'] else 'None'}")

def _render_screen(lobby_state: Dict, token: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Render the current screen and get user input.
    
    Args:
        lobby_state: Current lobby state
        token: Optional current player's token
        
    Returns:
        tuple: (command, args, token) where:
            - command is the numeric choice (1-5)
            - args is any additional arguments (table name, player name)
            - token is the player's token (None if not connected)
    """
    _clear_screen()
    _output_lobby(lobby_state)
    
    if token:
        player = next((p for p in lobby_state["players"] if isinstance(p, dict) and p["uuid"] == token), None)
        if player:
            print(f"\nConnected as: {_format_player(player)}")
    
    _display_menu(token)
    return _get_user_input(token)

async def _handle_command(
    command: str,
    args: str,
    token: Optional[str],
    state: Dict,
    websocket_client: Any
) -> Tuple[bool, Optional[str], Dict]:
    """
    Handle a single command and return whether to exit and the new token state.
    
    Args:
        command: The command to execute (1-5)
        args: Additional arguments for the command
        token: Current player token
        state: Current lobby state
        websocket_client: WebSocket client instance
        
    Returns:
        tuple: (should_exit, new_token, new_state)
    """
    try:
        if command == "5":  # Connect player
            if not args:
                print("\nError: Player name required")
                print("Usage: 5 <name>")
                print("Example: 5 john")
            else:
                # Find player in lobby state
                for player in state["players"]:
                    if isinstance(player, dict) and player["name"] == args:
                        print("\nError: Player name already exists")
                        input("Press Enter to continue...")
                        return False, token, state
                
                from socket_adapter.client_adapter import send_message
                await send_message(websocket_client, 'player_connect', {'name': args, 'type': 'player'})
                print("\nConnecting...")
                # Wait a moment for the connection response and lobby update
                await asyncio.sleep(0.5)
                # Wait for server response to get player data
                await asyncio.sleep(0.5)
                # Get updated state which should include the new player
                from services.state import get_lobby_state
                new_state = get_lobby_state()
                # Find player to get token
                player = next((p for p in new_state["players"] 
                             if isinstance(p, dict) and 
                             p.get("name") == args and 
                             "uuid" in p), None)
                if player:
                    token = player["uuid"]
                else:
                    print("\nError: Failed to get player token")
                    input("Press Enter to continue...")
                return False, token, new_state
            return False, token, state
        
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
                        from socket_adapter.client_adapter import send_message
                        await send_message(websocket_client, 'create_table', {
                            'name': table_name,
                            'rounds': rounds
                        })
                        print("\nCreating table...")
                        # Wait for server to process and update state
                        await asyncio.sleep(0.5)
                        # Get fresh state after table creation
                        from services.state import get_lobby_state
                        new_state = get_lobby_state()
                        return False, token, new_state
            except ValueError:
                print("\nError: Number of rounds must be a valid positive number")
                print("Example: 1 mytable 3")
            # Wait a moment for the server to process and broadcast
            await asyncio.sleep(0.5)
            input("Press Enter to continue...")
            return False, token, state
        
        elif command == "2" and token:  # Join table
            if not args:
                print("\nError: Table name required")
            else:
                table = next((t for t in state["tables"] if t["tablename"].lower() == args.lower()), None)
                if table:
                    from socket_adapter.client_adapter import send_message
                    await send_message(websocket_client, 'join_table', {
                        'table_name': table["tablename"],
                        'player_token': token
                    })
                    print("\nJoining table...")
                    # Wait for server to process and update state
                    await asyncio.sleep(0.5)
                    # Get fresh state after joining table
                    from services.state import get_lobby_state
                    new_state = get_lobby_state()
                    return False, token, new_state
                else:
                    print(f"\nError: Table '{args}' not found")
            # Wait a moment for the server to process and broadcast
            await asyncio.sleep(0.5)
            input("Press Enter to continue...")
            return False, token, state
        
        elif command == "3" and token:  # Start table
            if not args:
                print("\nError: Table name required")
            else:
                table = next((t for t in state["tables"] if t["tablename"].lower() == args.lower()), None)
                if table:
                    from socket_adapter.client_adapter import send_message
                    await send_message(websocket_client, 'start_table', {
                        'table_name': table["tablename"]
                    })
                    print("\nStarting table...")
                    # Wait for server to process and update state
                    await asyncio.sleep(0.5)
                    # Get fresh state after starting table
                    from services.state import get_lobby_state
                    new_state = get_lobby_state()
                    return False, token, new_state
                else:
                    print(f"\nError: Table '{args}' not found")
            # Wait a moment for the server to process and broadcast
            await asyncio.sleep(0.5)
            input("Press Enter to continue...")
            return False, token, state
        
        elif command == "4":  # Exit
            print("\nGoodbye!")
            return True, token, state
            
        elif command == "6" and token:  # Refresh lobby status
            from socket_adapter.client_adapter import send_message
            from services.state import get_lobby_state
            
            # Send refresh request
            await send_message(websocket_client, 'get_lobby_status', {})
            print("\nRefreshing lobby status...")
            
            # Wait for server response and state update
            await asyncio.sleep(0.5)
            
            # Get fresh state after update
            new_state = get_lobby_state()
            
            input("Press Enter to continue...")
            return False, token, new_state  # Return new state instead of old state
        
        else:
            if not token and command != "5":
                print("\nError: Please connect first (option 5)")
            else:
                print("\nError: Invalid command")
            input("Press Enter to continue...")
            return False, token, state
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        input("Press Enter to continue...")
        return False, token, state

async def run_terminal_ui_adapter(websocket_client: Any, initial_token: Optional[str] = None) -> NoReturn:
    """
    Public API: Run the terminal UI adapter.
    This is the only public function that should be called from outside.
    
    Args:
        websocket_client: WebSocket client instance
        initial_token: Optional initial player token
    """
    state = create_empty_lobby()  # Local state
    token = initial_token
    
    while True:
        # Get user input
        command, args, token = _render_screen(state, token)
        
        # Handle command and get new state
        should_exit, token, state = await _handle_command(
            command, args, token, state, websocket_client
        )
        if should_exit:
            break
