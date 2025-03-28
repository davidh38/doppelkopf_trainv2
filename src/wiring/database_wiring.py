#!/usr/bin/env python3
"""
Database wiring module.
Provides factory functions for creating pre-configured data stores.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

# Type aliases
Store = Dict[str, Any]
GameRecord = Dict[str, Any]
PlayerRecord = Dict[str, Any]
TableRecord = Dict[str, Any]
UserRecord = Dict[str, Any]

def create_game_store() -> Store:
    """
    Create game state storage.
    Handles game history, player statistics, and match records.
    
    Returns:
        Game store state dictionary
    """
    store = {
        'games': [],  # List of game records
        'statistics': {},  # Player statistics
        'active_games': {}  # Currently running games
    }
    
    def save_game(game_data: GameRecord) -> None:
        """Save game record to store."""
        game_record = {
            **game_data,
            'timestamp': datetime.now().isoformat(),
            'id': f"game_{len(store['games'])}"
        }
        store['games'].append(game_record)
        
        # Update player statistics
        for player in game_data.get('players', []):
            if player['name'] not in store['statistics']:
                store['statistics'][player['name']] = {
                    'games_played': 0,
                    'wins': 0,
                    'total_score': 0
                }
            stats = store['statistics'][player['name']]
            stats['games_played'] += 1
            if player.get('winner', False):
                stats['wins'] += 1
            stats['total_score'] += player.get('score', 0)
    
    def get_game_history(player_name: Optional[str] = None) -> List[GameRecord]:
        """Get game history, optionally filtered by player."""
        if not player_name:
            return store['games']
        return [
            game for game in store['games']
            if any(p['name'] == player_name for p in game.get('players', []))
        ]
    
    def get_player_statistics(player_name: str) -> Dict[str, Any]:
        """Get statistics for specific player."""
        return store['statistics'].get(player_name, {
            'games_played': 0,
            'wins': 0,
            'total_score': 0
        })
    
    # Public API
    store['api'] = {
        'save_game': save_game,
        'get_game_history': get_game_history,
        'get_player_statistics': get_player_statistics
    }
    
    return store

def create_lobby_store() -> Store:
    """
    Create lobby state storage.
    Handles active tables, player sessions, and connection states.
    
    Returns:
        Lobby store state dictionary
    """
    store = {
        'tables': [],  # Active tables
        'sessions': {},  # Player sessions
        'history': []  # Table history
    }
    
    def create_table(table_data: TableRecord) -> str:
        """Create new table record."""
        table_id = f"table_{len(store['tables'])}"
        table_record = {
            **table_data,
            'id': table_id,
            'created_at': datetime.now().isoformat(),
            'status': 'waiting'
        }
        store['tables'].append(table_record)
        return table_id
    
    def update_table_status(table_id: str, status: str) -> None:
        """Update table status."""
        for table in store['tables']:
            if table['id'] == table_id:
                table['status'] = status
                if status == 'completed':
                    store['history'].append(table)
                    store['tables'].remove(table)
                break
    
    def get_active_tables() -> List[TableRecord]:
        """Get all active tables."""
        return store['tables']
    
    def get_table_history() -> List[TableRecord]:
        """Get historical table records."""
        return store['history']
    
    # Public API
    store['api'] = {
        'create_table': create_table,
        'update_table_status': update_table_status,
        'get_active_tables': get_active_tables,
        'get_table_history': get_table_history
    }
    
    return store

def create_user_store() -> Store:
    """
    Create user data storage.
    Handles user profiles, authentication, and preferences.
    
    Returns:
        User store state dictionary
    """
    store = {
        'users': {},  # User records
        'sessions': {},  # Active sessions
        'preferences': {}  # User preferences
    }
    
    def create_user(user_data: UserRecord) -> str:
        """Create new user record."""
        user_id = f"user_{len(store['users'])}"
        user_record = {
            **user_data,
            'id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        store['users'][user_id] = user_record
        return user_id
    
    def get_user(user_id: str) -> Optional[UserRecord]:
        """Get user record by ID."""
        return store['users'].get(user_id)
    
    def update_user(user_id: str, updates: Dict[str, Any]) -> None:
        """Update user record."""
        if user_id in store['users']:
            store['users'][user_id].update(updates)
    
    def set_preferences(user_id: str, preferences: Dict[str, Any]) -> None:
        """Set user preferences."""
        store['preferences'][user_id] = {
            **store['preferences'].get(user_id, {}),
            **preferences
        }
    
    def get_preferences(user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        return store['preferences'].get(user_id, {})
    
    # Public API
    store['api'] = {
        'create_user': create_user,
        'get_user': get_user,
        'update_user': update_user,
        'set_preferences': set_preferences,
        'get_preferences': get_preferences
    }
    
    return store
