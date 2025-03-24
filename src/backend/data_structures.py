# data_structures.py

# Player dictionary structure
player_dict = {
    "session": "",  # Unique session identifier for the current connection
    "name": "",     # Display name of the player
    "type": "",     # Player type: "human" or "computer"
    "uuid": ""      # Persistent unique identifier for the player across sessions
}

# Table dictionary structure
table_dict = {
    "tablename": "",  # Descriptive name of the table shown in the lobby
    "players": [],    # List of players currently at the table (up to 4)
    "status": "",     # Table status: "waiting" for players or "playing" a game
    "game": None      # Current game being played at the table
}

# Game dictionary structure
game_dict = {
    "rounds": 0,      # Total number of rounds to be played in this game
    "round": 0,       # Current round number (1-based index)
    "players": [],    # Players participating in the game
    "cards": {},      # Mapping of player UUIDs to their current hand of cards
    "tricks": [],     # History of all tricks played so far in the current round
    "current_player": "",  # UUID of the player whose turn it is
    "eligible_cards": [],  # Cards that the current player is allowed to play
    "mode": "",       # Game mode: "solo", "normal", etc.
    "round_phase": "",  # Current phase: "variant", "armut" (poverty), "playing"
    "eligible_announcements": {},  # Announcements each player can make (e.g., "re", "kontra")
    "round_scores": {}  # Current scores for each player in this round
}

# Card dictionary structure
card_dict = {
    "suit": "",       # Card suit
    "rank": "",       # Card rank
    "value": 0,       # Card point value
    "is_trump": False  # Whether the card is a trump card
}

# Constants for reference
PLAYER_TYPES = ["human", "computer"]
TABLE_STATUSES = ["waiting", "playing"]
GAME_MODES = ["normal", "solo"]
ROUND_PHASES = ["variant", "armut", "playing"]
