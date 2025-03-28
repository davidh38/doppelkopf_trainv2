"""
Client entry point.
Terminal-based client for connecting to game server.
"""
import asyncio
import json
from typing import NoReturn, Dict, Any, Optional
from src.config import get_client_config
from src.wiring.socket_client_wiring import create_lobby_socket_client, create_game_socket_client

# Type aliases
Connection = Dict[str, Any]

class TerminalClient:
    def __init__(self):
        self.config = get_client_config()
        self.lobby_connection: Optional[Connection] = None
        self.game_connection: Optional[Connection] = None
        self.player_name: Optional[str] = None
        self.current_table: Optional[str] = None
    
    async def connect_to_lobby(self) -> None:
        """Connect to lobby server."""
        url = f"ws://{self.config['server_host']}:{self.config['lobby_port']}"
        self.lobby_connection = await create_lobby_socket_client(url)
        print("Connected to lobby server")
    
    async def connect_to_game(self, table_name: str) -> None:
        """Connect to game server for specific table."""
        url = f"ws://{self.config['server_host']}:{self.config['game_port']}"
        self.game_connection = await create_game_socket_client(url)
        self.current_table = table_name
        print(f"Connected to game server for table: {table_name}")
    
    async def handle_command(self, command: str) -> bool:
        """
        Handle user command.
        Returns False if client should exit, True otherwise.
        """
        parts = command.strip().split()
        if not parts:
            return True
            
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "quit":
            return False
            
        elif cmd == "help":
            self.print_help()
            
        elif cmd == "name":
            if len(args) != 1:
                print("Usage: name <player_name>")
                return True
            self.player_name = args[0]
            print(f"Set player name to: {self.player_name}")
            
        elif cmd == "create":
            if not self.player_name:
                print("Please set your name first using: name <player_name>")
                return True
            if len(args) != 1:
                print("Usage: create <table_name>")
                return True
                
            await self.lobby_connection.send_message("table_create", {
                "name": args[0],
                "creator": self.player_name
            })
            print(f"Created table: {args[0]}")
            
        elif cmd == "join":
            if not self.player_name:
                print("Please set your name first using: name <player_name>")
                return True
            if len(args) != 1:
                print("Usage: join <table_name>")
                return True
                
            # Join table in lobby
            await self.lobby_connection.send_message("player_join", {
                "player": self.player_name,
                "table": args[0]
            })
            
            # Connect to game server for this table
            await self.connect_to_game(args[0])
            
        elif cmd == "list":
            await self.lobby_connection.send_message("list_tables", {})
            
        else:
            print(f"Unknown command: {cmd}")
            self.print_help()
            
        return True
    
    def print_help(self) -> None:
        """Print available commands."""
        print("\nAvailable commands:")
        print("  name <player_name>  - Set your player name")
        print("  create <table_name> - Create a new game table")
        print("  join <table_name>   - Join an existing table")
        print("  list               - List available tables")
        print("  help               - Show this help message")
        print("  quit               - Exit the client\n")

async def run_client() -> NoReturn:
    """Run the terminal client."""
    client = TerminalClient()
    
    try:
        await client.connect_to_lobby()
        client.print_help()
        
        while True:
            command = input("> ")
            should_continue = await client.handle_command(command)
            if not should_continue:
                break
                
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanup connections
        if client.game_connection:
            await client.game_connection.disconnect()
        if client.lobby_connection:
            await client.lobby_connection.disconnect()

def main() -> NoReturn:
    """Main entry point."""
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
