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

def play_table_rounds(table: Dict) -> Dict:
    """
    Play all rounds for a table.
    
    Args:
        table: The table to play rounds for
        
    Returns:
        Updated table with all rounds completed
        
    This function manages the complete lifecycle of a table by:
    1. Getting the number of rounds to play from table settings
    2. Calling gameflow() for each round
    3. Returning the final table state with all rounds
    """
    num_rounds = table.get("num_rounds", 1)
    for _ in range(num_rounds):
        table = gameflow(table)
        if table["status"] == "closed":
            break
    return table

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
        "tricks": {},          # Played tricks
        "score": {},          # Round scores
        "start_time": datetime.now(),  # Round start
        "end_time": None,     # Round end
        "players": players,    # Participating players
        "final_score": {}     # Final round score
    }

def gameflow(table: Dict) -> Dict:
    """
    Manages the game flow for a table through all phases.
    
    Args:
        table: The table to manage game flow for
        
    Returns:
        Updated table with new game state
        
    Flow:
    1. Game Initialization
       - Create and shuffle cards
       - Distribute to players
       - Determine first player
    
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
    # Create new states for each phase instead of mutating
    game = create_initial_game_state(table["players"])
    game = initialize_game(game)
    game = handle_variant_phase(game)
    game = handle_poverty_phase(game) if game["mode"] == "armut" else game
    game = play_all_tricks(game)
    game = finalize_game(game)
    
    # Create new table state with updated rounds
    return create_updated_table(table, game)

def initialize_game(game: Dict) -> Dict:
    """Initialize game state with cards and first player"""
    cards = create_cards()
    shuffled_cards = shuffle_cards(cards)
    distributed_cards = distribute_cards(shuffled_cards, game["players"])
    first_player = determine_first_player(game["players"])
    
    return {
        **game,
        "cards": distributed_cards,
        "current_player": first_player
    }

def handle_variant_phase(game: Dict) -> Dict:
    """Handle variant selection phase"""
    return {
        **game,
        "mode": "normal"  # For now, always normal mode
    }

def play_all_tricks(game: Dict) -> Dict:
    """Play all tricks in a functional way"""
    game_with_phase = {**game, "phase": "playing"}
    return reduce(play_trick, range(10), game_with_phase)

def finalize_game(game: Dict) -> Dict:
    """Calculate final scores and end game"""
    scores = calculate_round_score(game)
    return {
        **game,
        "score": scores,
        "final_score": scores,
        "end_time": datetime.now()
    }

def create_updated_table(table: Dict, game: Dict) -> Dict:
    """Create new table state with updated rounds"""
    new_rounds = table["rounds"] + (game,)
    return {
        **table,
        "rounds": new_rounds,
        "status": "waiting" if len(new_rounds) < table.get("num_rounds", 1) else "closed"
    }

def create_cards() -> Tuple[Dict, ...]:
    """Create a complete deck of Doppelkopf cards"""
    suits = ("hearts", "spades", "diamonds", "clubs")
    ranks = (
        ("ace", 11), ("ten", 10), ("king", 4),
        ("queen", 3), ("jack", 2)  # Removed nine to get 40 cards total (10 per player)
    )
    
    # Create all cards in a functional way using list comprehension
    return tuple(
        create_card(suit, rank, value, (suit == "diamonds") or (suit == "clubs" and rank == "queen"))
        for _ in range(2)  # Each card appears twice
        for suit in suits
        for rank, value in ranks
    )

def shuffle_cards(cards: Tuple[Dict, ...]) -> Tuple[Dict, ...]:
    """Create new shuffled tuple of cards"""
    shuffled = list(cards)  # Convert to list for shuffling
    random.shuffle(shuffled)
    return tuple(shuffled)  # Convert back to immutable tuple

def distribute_cards(cards: Tuple[Dict, ...], players: Tuple[Dict, ...]) -> Dict[str, Tuple[Dict, ...]]:
    """Distribute cards to players, returning new immutable state"""
    if not players or not cards:
        return {}
    
    cards_per_player = len(cards) // len(players)
    return {
        player["uuid"]: tuple(cards[i * cards_per_player:(i + 1) * cards_per_player])
        for i, player in enumerate(players)
    }

def determine_first_player(players: Tuple[Dict, ...]) -> str:
    """Determine which player goes first"""
    return random.choice(players)["uuid"] if players else ""

def handle_poverty_phase(game: Dict) -> Dict:
    """Handle poverty phase, returning new state"""
    return game  # For now, no changes

def play_trick(game: Dict, trick_number: int) -> Dict:
    """Play a single trick, returning new state"""
    # Create new tricks state with this trick
    new_tricks = {**game["tricks"], trick_number: ()}
    
    # Create new teams state if needed
    new_teams = (
        assign_teams(game["players"])
        if trick_number == 0 else
        game["player_teams"]
    )
    
    return {
        **game,
        "tricks": new_tricks,
        "player_teams": new_teams
    }

def assign_teams(players: Tuple[Dict, ...]) -> Dict[str, str]:
    """Assign teams to players, returning new teams state"""
    player_uuids = [p["uuid"] for p in players]
    random.shuffle(player_uuids)
    
    return {
        player_uuids[0]: "re",
        player_uuids[1]: "re",
        player_uuids[2]: "kontra",
        player_uuids[3]: "kontra"
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
