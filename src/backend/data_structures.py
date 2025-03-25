# data_structures.py

from typing import List, Optional, Dict, Any

# Type definitions using simple dict types
PlayerType = Dict[str, str]  # {session: str, name: str, type: str, uuid: str}

TableType = Dict[str, Any]  # {
                           #   tablename: str,
                           #   players: List[str],
                           #   status: str,
                           #   rounds: Optional[List],
                           #   num_rounds: int,
                           #   game_dict: str
                           # }

LobbyStatusType = Dict[str, List[Any]]  # {
                                       #   players: List[str],
                                       #   tables: List[TableType]
                                       # }

# Constants for reference
PLAYER_TYPES = ["human", "computer"]
TABLE_STATUSES = ["waiting", "running", "closed"]
GAME_MODES = ["normal", "solo"]
ROUND_PHASES = ["variant", "armut", "playing"]
ANNOUNCEMENT_TYPES = ["re", "kontra", "no90", "no60", "no30", "schwarz"]
TEAM_TYPES = ["re", "kontra", "unknown"]
