#!/usr/bin/env python3
"""
Service wiring module.
Provides factory functions for creating integrated server environment.
"""
from typing import Dict, Any, Callable
from datetime import datetime
from .socket_server_wiring import create_server
from .database_wiring import create_game_store, create_lobby_store, create_user_store

# Type aliases
Service = Dict[str, Any]
Store = Dict[str, Any]
Server = Dict[str, Any]

async def wire_service(game_store: Store, lobby_store: Store, socket_server: Server) -> Service:
    """
    Wire game and lobby logic with storage and networking.

    Args:
        game_store: Game data store
        lobby_store: Lobby data store
        socket_server: WebSocket server instance

    Returns:
        Integrated service
    """
    service = {
        'game_store': game_store,
        'lobby_store': lobby_store,
        'server': socket_server,
        'active_games': {}
    }

    async def handle_game_end(game_id: str, game_data: dict) -> None:
        """Handle game completion."""
        # Save game record
        game_store['api']['save_game']({
            **game_data,
            'completed_at': datetime.now().isoformat()
        })

        # Clean up active game
        if game_id in service['active_games']:
            del service['active_games'][game_id]

        # Notify clients
        await socket_server['api']['broadcast_message'](
            'game_result',
            game_data
        )

    async def handle_game_action(game_id: str, action_data: dict) -> None:
        """Process game action."""
        if game_id not in service['active_games']:
            return

        game = service['active_games'][game_id]

        # Update game state
        game['last_action'] = action_data

        # Check for game completion
        if action_data.get('type') == 'game_over':
            await handle_game_end(game_id, {
                **game,
                'winner': action_data.get('winner'),
                'final_score': action_data.get('score')
            })
        else:
            # Notify clients of state update
            await socket_server['api']['broadcast_message'](
                'game_update',
                {'game_id': game_id, 'state': game}
            )

    async def handle_table_creation(table_data: dict) -> str:
        """Handle table creation request."""
        from services.lobby_table_handler import handle_create_table
        
        # Get current lobby state
        current_state = {
            "players": [],
            "tables": lobby_store['api']['get_active_tables']()
        }
        
        # Use pure handler function
        result = handle_create_table(current_state, table_data["name"], table_data.get("rounds", 1))
        
        if not result[0]:  # If failed
            raise ValueError(result[2])  # Raise error message
            
        new_state, table = result[1]
        
        # Create table record
        table_id = lobby_store['api']['create_table'](table)
        
        # Notify clients
        await socket_server['api']['broadcast_message'](
            'table_created',
            {
                'table_id': table_id,
                **table
            }
        )
        
        return table_id

    async def handle_table_update(table_id: str, update_data: dict) -> None:
        """Handle table state update."""
        from services.lobby_table_handler import handle_start_table
        
        # Get current state
        current_state = {
            "players": [],
            "tables": lobby_store['api']['get_active_tables']()
        }
        
        # Find target table
        target_table = next((t for t in current_state["tables"] if t["id"] == table_id), None)
        if not target_table:
            raise ValueError("Table not found")
            
        # Use pure handler function
        result = handle_start_table(current_state, target_table)
        
        if not result[0]:  # If failed
            raise ValueError(result[2])
            
        # Update table status
        lobby_store['api']['update_table_status'](
            table_id,
            update_data.get('status', 'waiting')
        )
        
        # Get updated table list
        tables = lobby_store['api']['get_active_tables']()
        
        # Notify clients
        await socket_server['api']['broadcast_message'](
            'lobby_update',
            {'tables': tables}
        )

    async def handle_player_join(table_id: str, player_data: dict) -> None:
        """Handle player joining table."""
        from services.lobby_table_handler import handle_add_player_to_table
        
        # Get current state
        current_state = {
            "players": [],
            "tables": lobby_store['api']['get_active_tables']()
        }
        
        # Find target table
        target_table = next((t for t in current_state["tables"] if t["id"] == table_id), None)
        if not target_table:
            raise ValueError("Table not found")
            
        # Use pure handler function
        result = handle_add_player_to_table(current_state, target_table, player_data["name"])
        
        if not result[0]:  # If failed
            raise ValueError(result[2])
            
        new_state, updated_table = result[1]
        
        # Update table record
        tables = lobby_store['api']['get_active_tables']()
        for table in tables:
            if table['id'] == table_id:
                if 'players' not in table:
                    table['players'] = []
                table['players'].append(player_data)
                break
                
        # Notify clients
        await socket_server['api']['broadcast_message'](
            'player_joined',
            {
                'table_id': table_id,
                'player': player_data
            }
        )
        
        # Update lobby state
        await socket_server['api']['broadcast_message'](
            'lobby_update',
            {'tables': tables}
        )

    # Add service API
    service['api'] = {
        'handle_game_action': handle_game_action,
        'handle_game_end': handle_game_end,
        'handle_table_creation': handle_table_creation,
        'handle_table_update': handle_table_update,
        'handle_player_join': handle_player_join
    }

    return service

async def create_server_environment(port: int) -> Service:
    """
    Create complete server environment with all components.

    Args:
        port: Port number for WebSocket server

    Returns:
        Integrated service
    """
    # Create components
    game_store = create_game_store()
    lobby_store = create_lobby_store()
    user_store = create_user_store()
    socket_server = await create_server(port)

    # Wire everything together
    service = await wire_service(game_store, lobby_store, socket_server)

    # Add user store for authentication/preferences
    service['user_store'] = user_store

    return service
