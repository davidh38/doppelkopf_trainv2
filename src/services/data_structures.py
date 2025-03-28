# data_structures.py

from frozendict import frozendict
from typing import Dict, Tuple, Any, Union, Optional, TypedDict

class PlayerType(TypedDict):
    session: str
    name: str
    type: str
    uuid: str

class TableType(TypedDict):
    tablename: str
    players: Tuple[PlayerType, ...]
    rounds: Tuple[Dict, ...]
    status: str
    num_rounds: int
    game_dict: Any

class LobbyStatusType(TypedDict):
    players: Tuple[PlayerType, ...]
    tables: Tuple[TableType, ...]
from datetime import datetime

"""
Data structure definitions:

PlayerDict: {
    session: str  # Unique session identifier
    name: str     # Display name
    type: str     # "human" or "computer"
    uuid: str     # Persistent unique identifier
}

CardDict: {
    suit: str     # Card suit
    rank: str     # Card rank
    value: int    # Card point value
    is_trump: bool # Whether it's a trump card
}

AnnouncementDict: {
    player_id: str    # UUID of announcing player
    type: str        # Type of announcement
    card_number: int # After which card the announcement was made (0 means before first card)
    timestamp: datetime # When announced
}

GameDict: {
    cards: Dict[uuid, Tuple[CardDict, ...]]  # Player hands
    current_player: str                      # UUID of current player
    eligible_cards: Tuple[CardDict, ...]     # Playable cards
    mode: str                                # Game mode
    phase: str                               # Game phase
    eligible_announcements: Dict             # Possible announcements
    player_teams: Dict[str, str]            # Player team assignments
    announcements: Tuple[AnnouncementDict, ...] # Made announcements
    tricks: Dict[int, Tuple[Tuple[str, CardDict], ...]] # Played tricks
    score: Dict                             # Round scores
    start_time: datetime                    # Round start
    end_time: Optional[datetime]            # Round end
    players: Tuple[PlayerDict, ...]         # Participating players
    final_score: Dict                       # Final round score
}

TableDict: {
    tablename: str                    # Table name
    players: Tuple[PlayerDict, ...]   # Players at table
    rounds: Tuple[GameDict, ...]      # Played/playing rounds
    status: str                       # Table status
}

LobbyStatusDict: {
    players: Tuple[PlayerDict, ...]   # Connected players
    tables: Tuple[TableDict, ...]     # Active tables
}
"""

# Constants using immutable types
PLAYER_TYPES = ("human", "computer")
TABLE_STATUSES = ("waiting", "running", "closed")
GAME_MODES = ("normal", "solo")
GAME_PHASES = ("variant", "armut", "playing")
ANNOUNCEMENT_TYPES = ("re", "kontra", "no90", "no60", "no30", "schwarz")
TEAM_TYPES = ("re", "kontra", "unknown")

# Helper functions to create immutable instances
def create_player(session: str, name: str, type_: str, uuid: str) -> Dict:
    """Create an immutable player dictionary"""
    return frozendict({
        "session": session,
        "name": name,
        "type": type_,
        "uuid": uuid
    })

def create_card(suit: str, rank: str, value: int, is_trump: bool) -> Dict:
    """Create an immutable card dictionary"""
    return frozendict({
        "suit": suit,
        "rank": rank,
        "value": value,
        "is_trump": is_trump
    })

def create_announcement(player_id: str, type_: str, card_number: int, timestamp: datetime) -> Dict:
    """Create an immutable announcement dictionary"""
    return frozendict({
        "player_id": player_id,
        "type": type_,
        "card_number": card_number,
        "timestamp": timestamp
    })

def create_table(tablename: str, players: Tuple, rounds: Tuple, status: str) -> Dict:
    """Create an immutable table dictionary"""
    return frozendict({
        "tablename": tablename,
        "players": players,
        "rounds": rounds,
        "status": status
    })

def create_lobby_status(players: Tuple, tables: Tuple) -> Dict:
    """Create an immutable lobby status dictionary"""
    return frozendict({
        "players": players,
        "tables": tables
    })
