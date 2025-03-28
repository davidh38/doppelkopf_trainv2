import pytest
from datetime import datetime
from src.services.game_handler import gameflow
from src.services.data_structures import create_player, create_table

def test_gameflow_initialization():
    """Test that gameflow properly initializes a new game"""
    # Create test players
    players = (
        create_player("s1", "Player1", "human", "uuid1"),
        create_player("s2", "Player2", "human", "uuid2"),
        create_player("s3", "Player3", "human", "uuid3"),
        create_player("s4", "Player4", "human", "uuid4")
    )
    
    # Create test table
    table = create_table("Test Table", players, (), "waiting")
    
    # Run gameflow
    updated_table = gameflow(table)
    
    # Verify table was updated
    assert len(updated_table["rounds"]) == 1
    
    # Get the new game state
    game = updated_table["rounds"][0]
    
    # Verify game initialization
    assert game["phase"] == "playing"  # Should be in playing phase at end
    assert game["mode"] in ["normal", "solo", "armut"]
    assert game["start_time"] is not None
    assert game["end_time"] is not None
    assert game["players"] == players
    assert game["current_player"] in [p["uuid"] for p in players]
    
    # Verify card distribution
    assert len(game["cards"]) == 4  # Each player should have cards
    for player_uuid in [p["uuid"] for p in players]:
        assert player_uuid in game["cards"]
        player_cards = game["cards"][player_uuid]
        assert len(player_cards) == 10  # Each player should have 10 cards
    
    # Verify tricks were played
    assert len(game["tricks"]) == 10  # Should have played 10 tricks
    
    # Verify scoring
    assert game["score"] != {}
    assert game["final_score"] != {}

def test_gameflow_table_status_update():
    """Test that table status is updated correctly based on num_rounds"""
    players = (
        create_player("s1", "Player1", "human", "uuid1"),
        create_player("s2", "Player2", "human", "uuid2"),
        create_player("s3", "Player3", "human", "uuid3"),
        create_player("s4", "Player4", "human", "uuid4")
    )
    
    # Test single round table
    table = create_table("Test Table", players, (), "waiting")
    updated_table = gameflow(table)
    assert updated_table["status"] == "closed"  # Should close after one round
    
    # Test multi-round table
    table = {**table, "num_rounds": 3}
    updated_table = gameflow(table)
    assert updated_table["status"] == "waiting"  # Should stay open for more rounds

def test_gameflow_team_assignments():
    """Test that teams are properly assigned during gameplay"""
    players = (
        create_player("s1", "Player1", "human", "uuid1"),
        create_player("s2", "Player2", "human", "uuid2"),
        create_player("s3", "Player3", "human", "uuid3"),
        create_player("s4", "Player4", "human", "uuid4")
    )
    
    table = create_table("Test Table", players, (), "waiting")
    updated_table = gameflow(table)
    game = updated_table["rounds"][0]
    
    # Verify all players were assigned teams
    assert len(game["player_teams"]) == 4
    for team in game["player_teams"].values():
        assert team in ["re", "kontra"]  # No unknown teams at end of game
