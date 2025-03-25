# src/frontend/lobby_table_output.py

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
