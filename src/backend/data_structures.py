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
    "game": None,      # The table consists of a game_dict
    "rounds": 0       # Determines how many rounds a table will be played
}

# Announcement dictionary structure
announcement_dict = {
    "player_id": "",  # UUID of the player who made the announcement
    "type": "",       # Type of announcement (e.g., "re", "kontra", "no90", "no60", etc.)
    "trick_number": 0,  # At which trick the announcement was made (0 means before first trick)
    "timestamp": ""   # When the announcement was made
}

# Round dictionary structure
round_dict = {
    "players": [],       # Players participating in this round
    "cards": {},         # Mapping of player UUIDs to their current hand of cards
    "current_player": "",  # UUID of the player whose turn it is
    "eligible_cards": [],  # Cards that the current player is allowed to play
    "mode": "",          # Game mode: "solo", "normal", etc.
    "phase": "",         # Current phase: "variant", "armut" (poverty), "playing"
    "eligible_announcements": {},  # Announcements each player can make (e.g., "re", "kontra")
    "player_teams": {},  # Mapping of player UUIDs to their team assignment ("re", "kontra", "unknown")
    "announcements": [],  # List of all announcements made in this round
    "tricks": {},        # Tricks played in this round, keyed by trick number
                         # Each trick is a list of (player_id, card) tuples
    "score": {}          # Scores for this specific round
}

# Game dictionary structure
game_dict = {
    "rounds": {}, # Dictionary mapping round numbers (int) to round_dict objects
    # Example: {1: round_dict1, 2: round_dict2, ...}
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
ANNOUNCEMENT_TYPES = ["re", "kontra", "no90", "no60", "no30", "schwarz"]
TEAM_TYPES = ["re", "kontra", "unknown"]
