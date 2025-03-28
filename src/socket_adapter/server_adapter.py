#!/usr/bin/env python3
"""
Server adapter for WebSocket communication.
Handles client connections and message broadcasting.
"""
import json
import asyncio
import websockets
from typing import Dict, Set, Any, Tuple
from datetime import datetime
from websockets.server import WebSocketServerProtocol
from services.lobby_table_handler import (
    create_empty_lobby, handle_login_player,
    handle_create_table, handle_add_player_to_table, handle_start_table
)
from services.game_handler import create_initial_game_state

# Type aliases
ClientState = Tuple[WebSocketServerProtocol, datetime]  # (websocket, last_heartbeat)
Server = Dict[str, Any]

# Pure functions for state management

def create_server_state(port: int) -> Server:
    """Create immutable server state dictionary."""
    return {
        'port': port,
        'clients': set(),  # Set of ClientState tuples
        'running': False,
        'task': None
    }

def create_client_state(websocket: WebSocketServerProtocol) -> ClientState:
    """Create immutable client state tuple."""
    return (websocket, datetime.now())

# Message handling

async def send_message(websocket: WebSocketServerProtocol, msg_type: str, payload: dict) -> None:
    """Send message to client."""
    message = json.dumps({
        'type': msg_type,
        'payload': payload,
        'timestamp': datetime.now().timestamp()
    })
    await websocket.send(message)

async def broadcast_message(server: Server, msg_type: str, payload: dict) -> None:
    """Broadcast message to all connected clients."""
    if not server['running']:
        raise RuntimeError("Server is not running")
        
    message = json.dumps({
        'type': msg_type,
        'payload': payload,
        'timestamp': datetime.now().timestamp()
    })
    
    # Send to all connected clients
    for client in server['clients'].copy():
        try:
            await client[0].send(message)
        except websockets.exceptions.WebSocketException:
            server['clients'].remove(client)
            try:
                await client[0].close()
            except websockets.exceptions.WebSocketException:
                pass

# Server-side lobby state
_server_lobby = create_empty_lobby()

def get_server_lobby() -> Dict:
    """Get current server lobby state."""
    return _server_lobby

def set_server_lobby(state: Dict) -> None:
    """Update server lobby state."""
    global _server_lobby
    _server_lobby = state

async def handle_get_lobby_status(client: ClientState) -> None:
    """Handle lobby status request from client."""
    lobby_status = get_server_lobby()
    await send_message(client[0], 'lobby_update', lobby_status)

async def broadcast_lobby_status(server: Server) -> None:
    """Broadcast current lobby status to all clients."""
    lobby_status = get_server_lobby()
    await broadcast_message(server, 'lobby_update', lobby_status)

async def handle_client_message(server: Server, client: ClientState, message: str) -> ClientState:
    """Handle incoming client message."""
    try:
        data = json.loads(message)
        
        if data['type'] == 'disconnect':
            server['clients'].remove(client)
            await client[0].close()
            return client
            
        if data['type'] == 'get_lobby_status':
            await handle_get_lobby_status(client)
            return client
            
        # Handle state-changing messages
        if data['type'] == 'player_connect':
            current_state = get_server_lobby()
            result = handle_login_player(current_state, data['payload']['name'])
            if result[0]:  # success
                new_state, player = result[1]
                set_server_lobby(new_state)
                await send_message(client[0], 'player_connected', {'token': player['uuid']})
                await broadcast_lobby_status(server)  # Broadcast to all clients
            else:
                await send_message(client[0], 'error', {'message': result[2]})
            return client

        if data['type'] == 'create_table':
            current_state = get_server_lobby()
            result = handle_create_table(current_state, data['payload']['name'], data['payload']['rounds'])
            if result[0]:  # success
                new_state, table = result[1]
                set_server_lobby(new_state)
                await broadcast_lobby_status(server)
            else:
                await send_message(client[0], 'error', {'message': result[2]})
            return client

        if data['type'] == 'join_table':
            current_state = get_server_lobby()
            table = next((t for t in current_state["tables"] if t["tablename"] == data['payload']['table_name']), None)
            if table:
                result = handle_add_player_to_table(current_state, table, data['payload']['player_token'])
                if result[0]:  # success
                    new_state, updated_table = result[1]
                    set_server_lobby(new_state)
                    await broadcast_lobby_status(server)
                else:
                    await send_message(client[0], 'error', {'message': result[2]})
            else:
                await send_message(client[0], 'error', {'message': 'Table not found'})
            return client

        if data['type'] == 'start_table':
            current_state = get_server_lobby()
            table = next((t for t in current_state["tables"] if t["tablename"] == data['payload']['table_name']), None)
            if table:
                result = handle_start_table(current_state, table)
                if result[0]:  # success
                    new_state, updated_table = result[1]
                    set_server_lobby(new_state)
                    # Initialize game state
                    game_state = create_initial_game_state(tuple(
                        next(p for p in current_state["players"] if isinstance(p, dict) and p["uuid"] == player_token)
                        for player_token in updated_table["players"]
                    ))
                    updated_table["game_dict"] = game_state
                    await broadcast_lobby_status(server)
                else:
                    await send_message(client[0], 'error', {'message': result[2]})
            else:
                await send_message(client[0], 'error', {'message': 'Table not found'})
            return client
            
    except json.JSONDecodeError:
        await send_message(client[0], 'error', {'message': 'Invalid message format'})
        
    return client

async def handle_client(server: Server, websocket: WebSocketServerProtocol) -> None:
    """Handle client connection lifecycle."""
    client = create_client_state(websocket)
    server['clients'].add(client)
    
    # Send initial lobby status to new client
    await handle_get_lobby_status(client)
    
    try:
        while server['running'] and client in server['clients']:
            try:
                message = await websocket.recv()
                client = await handle_client_message(server, client, message)
            except websockets.exceptions.WebSocketException:
                break
    finally:
        if client in server['clients']:
            server['clients'].remove(client)
            await broadcast_lobby_status(server)

# Public API

async def create_server(port: int) -> Server:
    """Create WebSocket server instance."""
    return create_server_state(port)

async def start_server(server: Server) -> None:
    """Start WebSocket server."""
    if server['running']:
        raise RuntimeError("Server is already running")
    
    server['running'] = True
    
    async def serve():
        async with websockets.serve(
            lambda ws: handle_client(server, ws),
            'localhost',
            server['port']
        ):
            await asyncio.Future()  # run forever
    
    server['task'] = asyncio.create_task(serve())
    
    try:
        await server['task']
    except asyncio.CancelledError:
        pass
    finally:
        server['running'] = False

async def stop_server(server: Server) -> None:
    """Stop WebSocket server and disconnect all clients."""
    if not server['running']:
        return
        
    server['running'] = False
    
    # Disconnect all clients
    for client in server['clients'].copy():
        try:
            await client[0].close()
        except websockets.exceptions.WebSocketException:
            pass
        server['clients'].remove(client)
    
    # Cancel server task
    if server['task']:
        server['task'].cancel()
        try:
            await server['task']
        except asyncio.CancelledError:
            pass
