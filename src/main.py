"""
Main entry point for the application.
Determines which frontend to use based on configuration.
"""

from typing import NoReturn
from src.config import get_frontend_type, VALID_FRONTEND_TYPES
from src.backend.lobby_table_handler import get_lobby_status, login_player, create_table, add_player_to_table, start_table
from src.frontend.terminal.lobby_table_output import render_screen

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

def run_web_frontend() -> NoReturn:
    """Run the web frontend."""
    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"
    
    print("Web frontend selected")
    app.run(debug=True)

def main() -> NoReturn:
    """Main entry point."""
    frontend_runners = {
        'terminal': run_terminal_frontend,
        'web': run_web_frontend
    }
    
    frontend_type = get_frontend_type()
    runner = frontend_runners[frontend_type]
    runner()

if __name__ == '__main__':
    main()
