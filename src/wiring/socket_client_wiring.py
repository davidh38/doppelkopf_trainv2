#!/usr/bin/env python3
"""
Socket client wiring module.
Provides factory functions for creating pre-configured socket clients.
"""
from typing import Dict, Any, Callable
import json
from datetime import datetime
from ..socket_adapter.client_adapter import connect, disconnect, send_message, start_message_handler

# Type aliases
MessageHandler = Callable[[Dict[str, Any]], None]
MessageHandlers = Dict[str, MessageHandler]

def create_default_handlers() -> MessageHandlers:
    """Create default message handlers."""
    def handle_error(payload: dict) -> None:
        """Handle error messages from server."""
        print(f"Error: {payload.get('message', 'Unknown error')}")
    
    def handle_game_update(payload: dict) -> None:
        """Handle game state updates."""
        game_state = payload.get('gameState', {})
        players = payload.get('players', [])
        current_turn = payload.get('currentTurn', '')
        # Log update - in real implementation this would update UI
        print(f"Game update: {len(players)} players, current turn: {current_turn}")
    
    def handle_lobby_update(payload: dict) -> None:
        """Handle lobby state updates."""
        players = payload.get('players', [])
        tables = payload.get('tables', [])
        # Log update - in real implementation this would update UI
        print(f"Lobby update: {len(players)} players, {len(tables)} tables")
    
    return {
        'error': handle_error,
        'game_update': handle_game_update,
        'lobby_update': handle_lobby_update
    }

async def create_socket_client(url: str) -> dict:
    """
    Create and configure socket client with default handlers.
    
    Args:
        url: WebSocket server URL
        
    Returns:
        Configured client connection state
    """
    connection = await connect(url)
    handlers = create_default_handlers()
    await start_message_handler(connection, handlers)
    return connection

async def create_game_socket_client(url: str) -> dict:
    """
    Create socket client configured for game-specific message handling.
    
    Args:
        url: WebSocket server URL
        
    Returns:
        Configured client connection state
    """
    connection = await connect(url)
    
    # Game-specific handlers
    def handle_player_turn(payload: dict) -> None:
        """Handle player turn notifications."""
        player = payload.get('player', '')
        action = payload.get('action', '')
        print(f"Player {player} performed {action}")
    
    def handle_game_result(payload: dict) -> None:
        """Handle game end results."""
        winner = payload.get('winner', '')
        score = payload.get('score', 0)
        print(f"Game ended. Winner: {winner}, Score: {score}")
    
    handlers = {
        **create_default_handlers(),
        'player_turn': handle_player_turn,
        'game_result': handle_game_result
    }
    
    await start_message_handler(connection, handlers)
    return connection

async def create_lobby_socket_client(url: str) -> dict:
    """
    Create socket client configured for lobby management.
    
    Args:
        url: WebSocket server URL
        
    Returns:
        Configured client connection state
    """
    connection = await connect(url)
    
    # Lobby-specific handlers
    def handle_table_created(payload: dict) -> None:
        """Handle table creation notifications."""
        table_name = payload.get('name', '')
        creator = payload.get('creator', '')
        print(f"Table '{table_name}' created by {creator}")
    
    def handle_player_joined(payload: dict) -> None:
        """Handle player join notifications."""
        player = payload.get('player', '')
        table = payload.get('table', '')
        print(f"Player {player} joined table '{table}'")
    
    handlers = {
        **create_default_handlers(),
        'table_created': handle_table_created,
        'player_joined': handle_player_joined
    }
    
    await start_message_handler(connection, handlers)
    return connection
