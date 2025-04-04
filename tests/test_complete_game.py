import pytest
from typing import Dict, List, Tuple
from src.services.lobby_table_handler import (
    create_empty_lobby,
    handle_login_player,
    handle_create_table,
    handle_add_player_to_table,
    handle_start_table
)
from src.services.game_handler import gameflow

def test_complete_two_round_game():
    """
    Test a complete game with 4 players playing 2 rounds.
    This test simulates the entire game flow without frontend interaction.
    """
    # Initialize empty lobby state
    lobby_state = create_empty_lobby()
    
    # Create and login 4 players
    players = []
    for i in range(4):
        player_name = f"Player{i+1}"
        result = handle_login_player(lobby_state, player_name)
        assert result[0], f"Failed to login player: {result[2]}"  # Check success and error message
        lobby_state, player = result[1]
        players.append(player)
        assert player in lobby_state["players"]
    
    # Create table with 2 rounds
    result = handle_create_table(lobby_state, "TestTable", 2)
    assert result[0], f"Failed to create table: {result[2]}"
    lobby_state, table = result[1]
    assert table in lobby_state["tables"]
    
    # Convert table to mutable dict and ensure players is a tuple
    table = dict(table)
    table["players"] = tuple(p for p in players)  # Convert list to tuple explicitly
    
    # Start table
    result = handle_start_table(lobby_state, table)
    assert result[0], f"Failed to start table: {result[2]}"
    lobby_state, table = result[1]
    assert table["status"] == "playing"
    
    # Play first round
    updated_table = gameflow(table)
    first_round = updated_table["rounds"][-1]
    
    # Verify first round
    assert first_round["phase"] == "complete"
    assert len(first_round["tricks"]) == 10
    assert first_round["final_score"] is not None
    assert all(player["uuid"] in first_round["player_teams"] for player in players)
    
    # Play second round
    final_table = gameflow(updated_table)
    second_round = final_table["rounds"][-1]
    
    # Verify second round
    assert second_round["phase"] == "complete"
    assert len(second_round["tricks"]) == 10
    assert second_round["final_score"] is not None
    assert all(player["uuid"] in second_round["player_teams"] for player in players)
    
    # Verify table completion
    assert final_table["status"] == "closed"
    assert len(final_table["rounds"]) == 2
    
    # Verify both rounds had different teams
    first_round_teams = first_round["player_teams"]
    second_round_teams = second_round["player_teams"]
    assert first_round_teams != second_round_teams, "Teams should be reshuffled between rounds"
    
    # Verify scoring
    for round_data in [first_round, second_round]:
        re_players = [p for p, team in round_data["player_teams"].items() if team == "re"]
        kontra_players = [p for p, team in round_data["player_teams"].items() if team == "kontra"]
        
        assert len(re_players) > 0, "Should have Re team players"
        assert len(kontra_players) > 0, "Should have Kontra team players"
        
        # Verify scores were calculated
        assert round_data["score"]["re"] >= 0
        assert round_data["score"]["kontra"] >= 0
        assert round_data["final_score"]["re"] >= 0
        assert round_data["final_score"]["kontra"] >= 0

def test_game_state_transitions():
    """
    Test that game states transition correctly through a complete round.
    """
    # Initialize empty lobby state
    lobby_state = create_empty_lobby()
    
    # Create and login 4 players
    players = []
    for i in range(4):
        result = handle_login_player(lobby_state, f"Player{i+1}")
        assert result[0], f"Failed to login player: {result[2]}"
        lobby_state, player = result[1]
        players.append(player)
    
    # Create table
    result = handle_create_table(lobby_state, "TestTable", 1)
    assert result[0], f"Failed to create table: {result[2]}"
    lobby_state, table = result[1]
    
    # Convert table to mutable dict and add players
    table = dict(table)
    table["players"] = tuple(p for p in players)  # Convert list to tuple explicitly
    
    # Start table
    result = handle_start_table(lobby_state, table)
    assert result[0], f"Failed to start table: {result[2]}"
    lobby_state, table = result[1]
    
    # Play through game
    final_table = gameflow(table)
    game = final_table["rounds"][0]
    
    # Verify game progression
    assert game["phase"] == "complete"
    assert game["start_time"] is not None
    assert game["end_time"] is not None
    assert len(game["tricks"]) == 10
    
    # Verify card distribution
    for player in players:
        assert player["uuid"] in game["cards"]
        assert len(game["cards"][player["uuid"]]) == 0  # All cards should be played
    
    # Verify trick structure
    for trick in game["tricks"]:
        assert len(trick) == 4  # Each trick should have 4 cards
        for play in trick:
            assert "player" in play
            assert "card" in play
            assert play["player"] in [p["uuid"] for p in players]
