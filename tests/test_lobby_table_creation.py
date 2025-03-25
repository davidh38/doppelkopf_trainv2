import pytest
from src.backend.lobby_table_handler import (
    connect_player,
    login_player,
    create_table,
    add_player_to_table,
    get_lobby_status,
    reset_lobby_status
)
from src.backend.data_structures import Player, Table


def test_lobby_table_creation():
    """
    Test case to create a lobby, connect players, login players,
    create a table, and add players to the table.
    """
    # Use the reset function to initialize lobby_status with empty lists
    reset_lobby_status()

    # 1. Connect player
    connect_player("test_token_1")
    current_status = get_lobby_status()
    assert "test_token_1" in current_status.players

    # 2. Login player
    player1 = login_player("player1")
    current_status = get_lobby_status()
    assert player1 in current_status.players

    # 3. Connect player
    connect_player("test_token_2")
    current_status = get_lobby_status()
    assert "test_token_2" in current_status.players

    # 4. Login player
    player2 = login_player("player2")
    current_status = get_lobby_status()
    assert player2 in current_status.players

    # 5. Create table
    table = create_table("table1", 5)
    current_status = get_lobby_status()
    assert table in current_status.tables

    # 6. Add player to table
    assert add_player_to_table(table, player1.name) is True
    
    # Verify the player was added to the table in lobby_status
    current_status = get_lobby_status()
    updated_table = next((t for t in current_status.tables if t.tablename == table.tablename), None)
    assert player1.name in updated_table.players

    # 7. Add player to table
    assert add_player_to_table(table, player2.name) is True
    
    # Verify the player was added to the table in lobby_status
    current_status = get_lobby_status()
    updated_table = next((t for t in current_status.tables if t.tablename == table.tablename), None)
    assert player2.name in updated_table.players
