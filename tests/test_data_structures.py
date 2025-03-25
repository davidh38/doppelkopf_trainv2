import pytest
from datetime import datetime
from src.backend.data_structures import (
    create_player,
    create_card,
    create_announcement,
    create_table,
    create_lobby_status,
    PLAYER_TYPES,
    TABLE_STATUSES
)

def test_create_player_immutable():
    player = create_player("session1", "John", "human", "uuid1")
    with pytest.raises(TypeError):
        player["name"] = "Jane"  # Should fail - frozendict is immutable

def test_create_card_immutable():
    card = create_card("hearts", "ace", 11, True)
    with pytest.raises(TypeError):
        card["value"] = 10  # Should fail - frozendict is immutable

def test_create_announcement_immutable():
    now = datetime.now()
    announcement = create_announcement("player1", "re", 0, now)
    with pytest.raises(TypeError):
        announcement["type"] = "kontra"  # Should fail - frozendict is immutable

def test_create_table_immutable():
    players = ()  # Empty tuple
    rounds = ()   # Empty tuple
    table = create_table("table1", players, rounds, "waiting")
    with pytest.raises(TypeError):
        table["status"] = "running"  # Should fail - frozendict is immutable

def test_create_lobby_status_immutable():
    players = ()  # Empty tuple
    tables = ()   # Empty tuple
    lobby = create_lobby_status(players, tables)
    with pytest.raises(TypeError):
        lobby["players"] = (create_player("s1", "John", "human", "u1"),)  # Should fail

def test_player_type_validation():
    # Valid player type
    player = create_player("session1", "John", PLAYER_TYPES[0], "uuid1")
    assert player["type"] in PLAYER_TYPES

def test_table_status_validation():
    # Valid table status
    table = create_table("table1", (), (), TABLE_STATUSES[0])
    assert table["status"] in TABLE_STATUSES
