# data_structures.py

from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Lobbystatus dictionary structure
lobbystatus_dict: Dict[str, List[any]] = {
    "players": List[player_dict],
    "tables": List[table_dict],
}

# Player dictionary structure
player_dict: Dict[str, str] = {
    "session": "",  # Unique session identifier for the current connection
    "name": "",     # Display name of the player
    "type": "",     # Player type: "human" or "computer"
    "uuid": ""      # Persistent unique identifier for the player across sessions
}

# Table dictionary structure
table_dict = {
    "tablename": "",
    "players": List[player_dict],
    "rounds": List[round_dict],
    "status": str,
}

# Announcement dictionary structure
announcement_dict: Dict[str, any] = {
    "player_id": "",
    "type": "",
    "trick_number": int,
    "timestamp": datetime,
}

# Round dictionary structure
round_dict: Dict[str, any] = {
    "cards": Dict[str, List[card_dict]],
    "current_player": str,
    "eligible_cards": List[card_dict],
    "mode": str,
    "phase": str,
    "eligible_announcements": Dict[str, bool],
    "player_teams": Dict[str, str],
    "announcements": List[announcement_dict],
    "tricks": Dict[int, List[Tuple[str, card_dict]]],
    "score": Dict[str, int],
    "start_time": Optional[datetime],
    "end_time": Optional[datetime],
    "players": List[player_dict],
    "final_score": Dict[str, int],
}

# Card dictionary structure
card_dict: Dict[str, any] = {
    "suit": str,
    "rank": str,
    "value": int,
    "is_trump": bool,
}

# Constants for reference
PLAYER_TYPES = ["human", "computer"]
TABLE_STATUSES = ["waiting", "running", "closed"]
GAME_MODES = ["normal", "solo"]
ROUND_PHASES = ["variant", "armut", "playing"]
ANNOUNCEMENT_TYPES = ["re", "kontra", "no90", "no60", "no30", "schwarz"]
TEAM_TYPES = ["re", "kontra", "unknown"]
