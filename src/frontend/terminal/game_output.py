# src/frontend/terminal/game_output.py

from typing import Dict, List, Tuple, Optional, NoReturn
from src.backend.game_handler import (
    play_table_rounds, create_initial_game_state,
    gameflow, initialize_game, handle_variant_phase,
    play_all_tricks, finalize_game
)

def format_card(card: Dict) -> str:
    """Format a card for display"""
    suit_symbols = {
        "hearts": "♥",
        "diamonds": "♦",
        "clubs": "♣",
        "spades": "♠"
    }
    return f"{suit_symbols[card['suit']]}{card['rank']}"

def format_player(player: Dict) -> str:
    """Format player info for display"""
    return player["name"]

def clear_screen() -> None:
    """Clear the terminal screen"""
    print("\033[H\033[J")

def display_game_state(game: Dict) -> None:
    """Display the current game state"""
    clear_screen()
    print("Game State:")
    print(f"Phase: {game['phase']}")
    
    # Show current player
    current_player = next(p for p in game['players'] if p['uuid'] == game['current_player'])
    print(f"Current Player: {format_player(current_player)}")
    
    # Show game mode
    print(f"Game Mode: {game['mode']}")
    
    # Show teams if known
    print("\nTeams:")
    for player in game['players']:
        team = game['player_teams'].get(player['uuid'], 'Unknown')
        print(f"  {format_player(player)}: {team}")
    
    # Show announcements if any
    if game['announcements']:
        print("\nAnnouncements:")
        for announcement in game['announcements']:
            print(f"  - {announcement}")
    print()

def display_player_hand(cards: List[Dict], eligible_cards: Optional[List[Dict]] = None) -> None:
    """Display a player's hand with eligible cards highlighted"""
    print("Your Hand:")
    for i, card in enumerate(cards, 1):
        card_str = format_card(card)
        if eligible_cards and card in eligible_cards:
            print(f"  {i}. [{card_str}]")  # Highlight eligible cards
        else:
            print(f"  {i}.  {card_str}")

def display_trick(trick: List[Dict]) -> None:
    """Display the current trick"""
    print("\nCurrent Trick:")
    if not trick:
        print("  (No cards played yet)")
        return
    
    for card_info in trick:
        player = card_info['player']
        card = card_info['card']
        print(f"  {format_player(player)}: {format_card(card)}")

def display_scores(scores: Dict) -> None:
    """Display the current scores"""
    print("\nScores:")
    for team, score in scores.items():
        print(f"  {team}: {score} points")

def get_player_input(prompt: str, valid_options: List[str]) -> str:
    """Get and validate player input"""
    while True:
        user_input = input(f"{prompt}: ").strip()
        if user_input in valid_options:
            return user_input
        print(f"Invalid input. Please choose from: {', '.join(valid_options)}")

def handle_variant_selection(game: Dict, player_token: str) -> str:
    """Handle the variant selection phase for a player"""
    if game['current_player'] != player_token:
        return "pass"
    
    print("\nVariant Selection Phase")
    print("Available variants:")
    print("1. Normal")
    print("2. Solo")
    print("3. Pass")
    
    choice = get_player_input(
        "Select variant",
        ["1", "2", "3"]
    )
    
    variant_map = {
        "1": "normal",
        "2": "solo",
        "3": "pass"
    }
    return variant_map[choice]

def handle_card_play(game: Dict, player_token: str) -> Optional[Dict]:
    """Handle playing a card"""
    if game['current_player'] != player_token:
        return None
    
    player_cards = game['cards'][player_token]
    eligible_cards = game['eligible_cards']
    
    display_player_hand(player_cards, eligible_cards)
    
    valid_options = [str(i) for i in range(1, len(player_cards) + 1)]
    choice = get_player_input(
        "Choose a card to play (number)",
        valid_options
    )
    
    return player_cards[int(choice) - 1]

def run_game_interface(table: Dict, player_token: str) -> NoReturn:
    """Run the game interface for a player"""
    print("\nGame starting...")
    input("Press Enter to continue...")
    
    game = table['rounds'][-1]  # Get current round
    
    while game['phase'] != 'complete':
        display_game_state(game)
        
        if game['phase'] == 'variant':
            variant = handle_variant_selection(game, player_token)
            if variant != "pass":
                game = handle_variant_phase(game)
        
        elif game['phase'] == 'playing':
            display_trick(game['tricks'].get(len(game['tricks']) - 1, []))
            card = handle_card_play(game, player_token)
            if card:
                # Update game state with played card
                game = play_all_tricks(game)
        
        # Show scores after each action
        if game.get('score'):
            display_scores(game['score'])
        
        input("\nPress Enter to continue...")
    
    # Show final scores
    clear_screen()
    print("Game Complete!")
    display_scores(game['final_score'])
    input("\nPress Enter to return to lobby...")
