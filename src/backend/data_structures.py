# data_structures.py

from typing import List, Optional, NamedTuple
from datetime import datetime

class Player(NamedTuple):
    session: str
    name: str
    type: str
    uuid: str

class Table(NamedTuple):
    tablename: str
    players: List[str]
    status: str
    rounds: Optional[List]
    num_rounds: int
    game_dict: str

class LobbyStatus(NamedTuple):
    players: List[str]
    tables: List[Table]

# Constants for reference
PLAYER_TYPES = ["human", "computer"]
TABLE_STATUSES = ["waiting", "running", "closed"]
GAME_MODES = ["normal", "solo"]
ROUND_PHASES = ["variant", "armut", "playing"]
ANNOUNCEMENT_TYPES = ["re", "kontra", "no90", "no60", "no30", "schwarz"]
TEAM_TYPES = ["re", "kontra", "unknown"]
