# Game Handler
# This file will contain functions for game mechanics and state management

from typing import Dict, Tuple, List, Optional
from datetime import datetime
import random
from .data_structures import (
    create_player, create_table, create_card,
    GAME_MODES, GAME_PHASES, TEAM_TYPES
)

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
    # Initialize new game state
    game = {
        "cards": {},           # Player hands
        "current_player": "",  # UUID of current player
        "eligible_cards": (),  # Playable cards
        "mode": "normal",      # Game mode
        "phase": "variant",    # Game phase
        "eligible_announcements": {},  # Possible announcements
        "player_teams": {p["uuid"]: "unknown" for p in table["players"]},  # Player team assignments
        "announcements": (),   # Made announcements
        "tricks": {},          # Played tricks
        "score": {},          # Round scores
        "start_time": datetime.now(),  # Round start
        "end_time": None,     # Round end
        "players": table["players"],  # Participating players
        "final_score": {}     # Final round score
    }
    
    # 1. Game Initialization
    cards = create_cards()
    shuffled_cards = shuffle_cards(cards)
    game["cards"] = distribute_cards(shuffled_cards, table["players"])
    game["current_player"] = determine_first_player(table["players"])
    
    # 2. Variant Selection Phase
    game["mode"] = handle_variant_selection(game)
    
    # 3. Poverty (Armut) Phase
    if game["mode"] == "armut":
        game = handle_poverty_phase(game)
    
    # 4. Playing Phase
    game["phase"] = "playing"
    for trick_number in range(10):  # 10 tricks per round
        game = play_trick(game, trick_number)
        
        # After each trick, check if we need to update team assignments
        if not all_teams_known(game["player_teams"]):
            game["player_teams"] = update_team_assignments(game)
    
    # 5. Scoring Phase
    scores = calculate_round_score(game)
    game["score"] = scores
    game["final_score"] = scores  # For now, final score is same as round score
    game["end_time"] = datetime.now()
    
    # Update table with new game
    new_rounds = table["rounds"] + (game,)
    return {
        **table,
        "rounds": new_rounds,
        "status": "waiting" if len(new_rounds) < table.get("num_rounds", 1) else "closed"
    }

def create_cards() -> List[Dict]:
    """Create a complete deck of Doppelkopf cards"""
    suits = ["hearts", "spades", "diamonds", "clubs"]
    ranks = [
        ("ace", 11), ("ten", 10), ("king", 4),
        ("queen", 3), ("jack", 2)  # Removed nine to get 40 cards total (10 per player)
    ]
    
    cards = []
    # In Doppelkopf, each card appears twice
    for _ in range(2):
        for suit in suits:
            for rank, value in ranks:
                # Queens of clubs are always trump
                # All diamonds are trump
                is_trump = (suit == "diamonds") or (suit == "clubs" and rank == "queen")
                cards.append(create_card(suit, rank, value, is_trump))
    
    return cards

def shuffle_cards(cards: List[Dict]) -> List[Dict]:
    """Shuffle the deck of cards"""
    shuffled = list(cards)  # Create a copy to not modify original
    random.shuffle(shuffled)
    return shuffled

def distribute_cards(cards: List[Dict], players: Tuple[Dict, ...]) -> Dict[str, Tuple[Dict, ...]]:
    """Distribute cards to players"""
    if not players or not cards:
        return {}
    
    cards_per_player = len(cards) // len(players)  # Should be 10 cards per player
    distribution = {}
    
    for i, player in enumerate(players):
        start = i * cards_per_player
        end = start + cards_per_player
        distribution[player["uuid"]] = tuple(cards[start:end])
    
    return distribution

def determine_first_player(players: Tuple[Dict, ...]) -> str:
    """Determine which player goes first"""
    if not players:
        return ""
    # For now, randomly select first player
    return random.choice(players)["uuid"]

def handle_variant_selection(game: Dict) -> str:
    """Handle the variant selection phase"""
    # For now, always return normal game mode
    return "normal"

def handle_poverty_phase(game: Dict) -> Dict:
    """Handle the poverty (armut) phase if applicable"""
    return game

def play_trick(game: Dict, trick_number: int) -> Dict:
    """Play a single trick"""
    # For testing, just simulate trick completion
    game["tricks"][trick_number] = ()
    
    # Simulate team assignment (in real implementation this would be based on cards played)
    if trick_number == 0:
        player_uuids = [p["uuid"] for p in game["players"]]
        # Randomly assign two players to each team
        random.shuffle(player_uuids)
        game["player_teams"].update({
            player_uuids[0]: "re",
            player_uuids[1]: "re",
            player_uuids[2]: "kontra",
            player_uuids[3]: "kontra"
        })
    
    return game

def all_teams_known(player_teams: Dict[str, str]) -> bool:
    """Check if all player teams are known"""
    return all(team != "unknown" for team in player_teams.values())

def update_team_assignments(game: Dict) -> Dict[str, str]:
    """Update team assignments based on played cards"""
    return game["player_teams"]

def calculate_round_score(game: Dict) -> Dict:
    """Calculate the score for the round"""
    # For testing, return dummy scores for both teams
    return {
        "re": 2,
        "kontra": 1
    }
