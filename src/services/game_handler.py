# Game Handler
# This file will contain functions for game mechanics and state management

from typing import Dict, Tuple, List, Optional
from datetime import datetime
from functools import reduce
import random
from .data_structures import (
    create_player, create_table, create_card,
    GAME_MODES, GAME_PHASES, TEAM_TYPES
)

def play_round(table: Dict, _: int) -> Dict:
    """Play a single round and determine if more rounds should be played"""
    if table["status"] == "closed":
        return table
    return gameflow(table)

def play_table_rounds(table: Dict) -> Dict:
    """
    Play all rounds for a table in a functional way.
    
    Args:
        table: The table to play rounds for
        
    Returns:
        Updated table with all rounds completed
        
    This function manages the complete lifecycle of a table by:
    1. Getting the number of rounds to play from table settings
    2. Using reduce to functionally apply gameflow() for each round
    3. Returning the final table state with all rounds
    """
    return reduce(
        play_round,
        range(table.get("num_rounds", 1)),
        table
    )

def create_initial_game_state(players: Tuple[Dict, ...]) -> Dict:
    """Create initial game state without any mutations"""
    return {
        "cards": {},           # Player hands
        "current_player": "",  # UUID of current player
        "eligible_cards": (),  # Playable cards
        "mode": "normal",      # Game mode
        "phase": "variant",    # Game phase
        "eligible_announcements": {},  # Possible announcements
        "player_teams": {p["uuid"]: "unknown" for p in players},  # Player team assignments
        "announcements": (),   # Made announcements
        "tricks": (),          # Played tricks as tuple of tuples
        "score": {},          # Round scores
        "start_time": datetime.now(),  # Round start
        "end_time": None,     # Round end
        "players": players,    # Participating players
        "final_score": {}     # Final round score
    }

def gameflow(table: Dict) -> Dict:
    """
    Manages the game flow for a table through all phases in a functional way.
    
    Args:
        table: The table to manage game flow for
        
    Returns:
        Updated table with new game state
        
    Flow:
    1. Game Initialization
       - Create and shuffle cards
       - Distribute to players
       - Determine first player
       - Assign initial teams
    
    2. Variant Selection Phase
       - Each player selects variant
       - Compute final game mode
    
    3. Poverty (Armut) Phase (if applicable)
       - Handle card exchanges
    
    4. Playing Phase (10 tricks)
       - For each trick:
         a. Get eligible cards for current player
         b. Current player plays card
         c. Update team assignments if needed
         d. Evaluate trick winner
         e. Set next player
         f. Handle any announcements
    
    5. Scoring Phase
       - Calculate round scores
       - Update game summary
    """
    initial_state = create_initial_game_state(table["players"])
    initial_state["player_teams"] = assign_teams(table["players"])  # Assign teams at start
    
    return create_updated_table(
        table,
        reduce(
            lambda game, fn: fn(game),
            [
                initialize_game,
                handle_variant_phase,
                lambda g: handle_poverty_phase(g) if g["mode"] == "armut" else g,
                play_all_tricks,
                finalize_game
            ],
            initial_state
        )
    )

def initialize_game(game: Dict) -> Dict:
    """Initialize game state with cards and first player in a functional way"""
    return {
        **game,
        "cards": distribute_cards(
            shuffle_cards(create_cards()),
            game["players"]
        ),
        "current_player": determine_first_player(game["players"])
    }

def handle_variant_phase(game: Dict) -> Dict:
    """Handle variant selection phase"""
    return {
        **game,
        "mode": "normal"  # For now, always normal mode
    }

def play_all_tricks(game: Dict) -> Dict:
    """Play all tricks in a functional way"""
    return reduce(
        play_trick,
        range(10),
        {**game, "phase": "playing"}
    )

def finalize_game(game: Dict) -> Dict:
    """Calculate final scores and end game in a functional way"""
    return {
        **game,
        "phase": "complete",
        "score": calculate_round_score(game),
        "final_score": calculate_round_score(game),
        "end_time": datetime.now()
    }

def create_updated_table(table: Dict, game: Dict) -> Dict:
    """Create new table state with updated rounds in a functional way"""
    current_rounds = table.get("rounds", ())
    if isinstance(current_rounds, list):
        current_rounds = tuple(current_rounds)
    elif current_rounds is None:
        current_rounds = ()
    return {
        **table,
        "rounds": current_rounds + (game,),
        "status": "waiting" if len(current_rounds) + 1 < table.get("num_rounds", 1) else "closed"
    }

def create_cards() -> Tuple[Dict, ...]:
    """Create a complete deck of Doppelkopf cards in a functional way"""
    return tuple(
        create_card(suit, rank, value, (suit == "diamonds") or (suit == "clubs" and rank == "queen"))
        for _ in range(2)  # Each card appears twice
        for suit in ("hearts", "spades", "diamonds", "clubs")
        for rank, value in (
            ("ace", 11), ("ten", 10), ("king", 4),
            ("queen", 3), ("jack", 2)  # Removed nine to get 40 cards total (10 per player)
        )
    )

def shuffle_cards(cards: Tuple[Dict, ...]) -> Tuple[Dict, ...]:
    """Create new shuffled tuple of cards in a functional way"""
    return tuple(random.sample(cards, len(cards)))

def distribute_cards(cards: Tuple[Dict, ...], players: Tuple[Dict, ...]) -> Dict[str, Tuple[Dict, ...]]:
    """Distribute cards to players in a functional way"""
    return {} if not players or not cards else {
        uuid: tuple(cards[i:i + len(cards) // len(players)])
        for i, uuid in enumerate(
            tuple(p["uuid"] for p in players),
            start=0
        )
    }

def determine_first_player(players: Tuple[Dict, ...]) -> str:
    """Determine which player goes first in a functional way"""
    return next((p["uuid"] for p in random.sample(players, 1)), "")

def handle_poverty_phase(game: Dict) -> Dict:
    """Handle poverty phase, returning new state"""
    return game  # For now, no changes

def play_trick(game: Dict, trick_number: int) -> Dict:
    """Play a single trick, returning new state in a functional way"""
    # Get current player's cards
    player_uuid = game["current_player"]
    player_cards = game["cards"][player_uuid]
    
    # If no cards left, skip this trick
    if not player_cards:
        return game
    
    # Play first card from player's hand
    played_card = player_cards[0]
    remaining_cards = player_cards[1:]
    
    # Create trick with all players playing their first card
    trick = []
    current_cards = game["cards"]
    current_player = player_uuid
    players_in_order = list(p["uuid"] for p in game["players"])
    start_idx = players_in_order.index(current_player)
    
    # Rotate player list so current player is first
    players_in_order = players_in_order[start_idx:] + players_in_order[:start_idx]
    
    # Each player plays one card
    for player_id in players_in_order:
        player_cards = current_cards[player_id]
        if not player_cards:  # Skip if player has no cards
            continue
        card = player_cards[0]
        trick.append({"player": player_id, "card": card})
        current_cards = {
            **current_cards,
            player_id: player_cards[1:]
        }
    
    # Find next player with cards
    next_player = None
    for player_id in players_in_order:
        if current_cards[player_id]:
            next_player = player_id
            break
    
    # If no player has cards, keep current player
    if next_player is None:
        next_player = current_player
    
    # Update game state
    return {
        **game,
        "tricks": game["tricks"] + (tuple(trick),),
        "cards": current_cards,
        "current_player": next_player
    }

def assign_teams(players: Tuple[Dict, ...]) -> Dict[str, str]:
    """Assign teams to players in a functional way"""
    player_uuids = tuple(p["uuid"] for p in players)
    # Randomly select 2 players for Re team
    re_players = tuple(random.sample(player_uuids, 2))
    return {
        uuid: "re" if uuid in re_players else "kontra"
        for uuid in player_uuids
    }

def all_teams_known(player_teams: Dict[str, str]) -> bool:
    """Check if all player teams are known"""
    return all(team != "unknown" for team in player_teams.values())

def calculate_round_score(game: Dict) -> Dict:
    """Calculate the score for the round"""
    return {
        "re": 2,
        "kontra": 1
    }
