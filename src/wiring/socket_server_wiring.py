#!/usr/bin/env python3
"""
Socket server wiring module.
Provides factory functions for creating pre-configured socket servers.
"""
from typing import Dict, Any, Callable
import json
from datetime import datetime
from ..socket_adapter.server_adapter import create_server, start_server, stop_server, broadcast_message

# Type aliases
Server = Dict[str, Any]
GameState = Dict[str, Any]

def create_game_state() -> GameState:
    """Create initial game state."""
    return {
        'players': [],
        'current_turn': None,
        'started': False,
        'completed': False
    }

async def create_game_server(port: int) -> Server:
    """
    Create and configure socket server for game handling.
    
    Args:
        port: Port number to listen on
        
    Returns:
        Configured server state
    """
    server = await create_server(port)
    game_state = create_game_state()
    
    async def handle_player_connect(server: Server, client: dict, payload: dict) -> None:
        """Handle player connection."""
        player_name = payload.get('name', '')
        if not player_name:
            return
            
        game_state['players'].append({
            'name': player_name,
            'connected': True,
            'ready': False
        })
        
        # Notify all clients of player join
        await broadcast_message(server, 'game_update', {
            'gameState': game_state,
            'players': game_state['players'],
            'currentTurn': game_state['current_turn']
        })
    
    async def handle_player_action(server: Server, client: dict, payload: dict) -> None:
        """Handle player game actions."""
        action = payload.get('action', '')
        player = payload.get('player', '')
        
        if not action or not player:
            return
            
        # Update game state based on action
        # In real implementation, this would validate and process game rules
        await broadcast_message(server, 'player_turn', {
            'player': player,
            'action': action
        })
    
    # Add message handlers to server
    server['handlers'] = {
        'player_connect': handle_player_connect,
        'player_action': handle_player_action
    }
    
    return server

async def create_lobby_server(port: int) -> Server:
    """
    Create socket server configured for lobby management.
    
    Args:
        port: Port number to listen on
        
    Returns:
        Configured server state
    """
    server = await create_server(port)
    lobby_state = {
        'tables': [],
        'players': []
    }
    
    async def handle_table_create(server: Server, client: dict, payload: dict) -> None:
        """Handle table creation requests."""
        table_name = payload.get('name', '')
        creator = payload.get('creator', '')
        rounds = payload.get('rounds', 1)
        
        if not table_name or not creator:
            return
            
        # Create new table
        table = {
            'name': table_name,
            'creator': creator,
            'players': [creator],
            'rounds': rounds,
            'status': 'waiting'
        }
        lobby_state['tables'].append(table)
        
        # Notify all clients
        await broadcast_message(server, 'table_created', {
            'name': table_name,
            'creator': creator,
            'rounds': rounds
        })
        
        # Update lobby state
        await broadcast_message(server, 'lobby_update', {
            'players': lobby_state['players'],
            'tables': lobby_state['tables']
        })
    
    async def handle_player_join(server: Server, client: dict, payload: dict) -> None:
        """Handle player join requests."""
        player = payload.get('player', '')
        table_name = payload.get('table', '')
        
        if not player or not table_name:
            return
            
        # Find and update table
        for table in lobby_state['tables']:
            if table['name'] == table_name:
                table['players'].append(player)
                
                # Notify all clients
                await broadcast_message(server, 'player_joined', {
                    'player': player,
                    'table': table_name
                })
                
                # Update lobby state
                await broadcast_message(server, 'lobby_update', {
                    'players': lobby_state['players'],
                    'tables': lobby_state['tables']
                })
                break
    
    # Add message handlers to server
    server['handlers'] = {
        'table_create': handle_table_create,
        'player_join': handle_player_join
    }
    
    return server
