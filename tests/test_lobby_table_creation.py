import pytest
from src.services.lobby_table_handler import (
    create_empty_lobby,
    handle_connect_player,
    handle_login_player,
    handle_create_table,
    handle_add_player_to_table
)

def test_lobby_table_creation():
    """
    Test case to create a lobby, connect players, login players,
    create a table, and add players to the table.
    """
    # Initialize empty lobby state
    lobby_state = create_empty_lobby()

    # 1. Connect player
    result = handle_connect_player(lobby_state, "test_token_1")
    assert result[0], f"Failed to connect player: {result[2]}"
    lobby_state = result[1]
    assert "test_token_1" in lobby_state["players"]

    # 2. Login player
    result = handle_login_player(lobby_state, "player1")
    assert result[0], f"Failed to login player: {result[2]}"
    lobby_state, player1 = result[1]
    assert player1 in lobby_state["players"]

    # 3. Connect player
    result = handle_connect_player(lobby_state, "test_token_2")
    assert result[0], f"Failed to connect player: {result[2]}"
    lobby_state = result[1]
    assert "test_token_2" in lobby_state["players"]

    # 4. Login player
    result = handle_login_player(lobby_state, "player2")
    assert result[0], f"Failed to login player: {result[2]}"
    lobby_state, player2 = result[1]
    assert player2 in lobby_state["players"]

    # 5. Create table
    result = handle_create_table(lobby_state, "table1", 5)
    assert result[0], f"Failed to create table: {result[2]}"
    lobby_state, table = result[1]
    assert table in lobby_state["tables"]

    # 6. Add player to table
    result = handle_add_player_to_table(lobby_state, table, player1["name"])
    assert result[0], f"Failed to add player to table: {result[2]}"
    lobby_state, table = result[1]
    assert player1["name"] in table["players"]

    # 7. Add player to table
    result = handle_add_player_to_table(lobby_state, table, player2["name"])
    assert result[0], f"Failed to add player to table: {result[2]}"
    lobby_state, table = result[1]
    assert player2["name"] in table["players"]
