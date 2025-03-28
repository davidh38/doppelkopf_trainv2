#!/usr/bin/env python3
"""
Server adapter for WebSocket communication.
Handles client connections and message broadcasting.
"""
import json
import asyncio
import websockets
from typing import Dict, Set, Any, Optional
from datetime import datetime
from websockets.server import WebSocketServerProtocol

# Type aliases
Server = Dict[str, Any]
Client = Dict[str, Any]
Clients = Set[Client]

def create_server_state(port: int) -> Server:
    """Create immutable server state dictionary."""
    return {
        'port': port,
        'clients': set(),
        'running': False,
        'task': None
    }

def create_client_state(websocket: WebSocketServerProtocol) -> Client:
    """Create immutable client state dictionary."""
    return {
        'websocket': websocket,
        'connected': True,
        'last_heartbeat': datetime.now()
    }

async def handle_client_message(server: Server, client: Client, message: str) -> None:
    """
    Handle incoming client message.
    
    Args:
        server: Server state dictionary
        client: Client state dictionary
        message: Raw message string
    """
    try:
        data = json.loads(message)
        
        # Handle system messages
        if data['type'] == 'ping':
            await client['websocket'].send(json.dumps({
                'type': 'pong',
                'payload': {},
                'timestamp': datetime.now().timestamp()
            }))
            client['last_heartbeat'] = datetime.now()
            return
            
        if data['type'] == 'disconnect':
            client['connected'] = False
            server['clients'].remove(client)
            await client['websocket'].close()
            return
            
    except json.JSONDecodeError:
        # Invalid message format
        await client['websocket'].send(json.dumps({
            'type': 'error',
            'payload': {'message': 'Invalid message format'},
            'timestamp': datetime.now().timestamp()
        }))

async def handle_client(server: Server, websocket: WebSocketServerProtocol) -> None:
    """
    Handle client connection lifecycle.
    
    Args:
        server: Server state dictionary
        websocket: Client WebSocket connection
    """
    client = create_client_state(websocket)
    server['clients'].add(client)
    
    try:
        while client['connected'] and server['running']:
            try:
                message = await websocket.recv()
                await handle_client_message(server, client, message)
            except websockets.exceptions.WebSocketException:
                break
    finally:
        client['connected'] = False
        if client in server['clients']:
            server['clients'].remove(client)
        try:
            await websocket.close()
        except websockets.exceptions.WebSocketException:
            pass

# Public API

async def create_server(port: int) -> Server:
    """
    Create WebSocket server instance.
    
    Args:
        port: Port number to listen on
        
    Returns:
        Server state dictionary
    """
    return create_server_state(port)

async def start_server(server: Server) -> None:
    """
    Start WebSocket server.
    
    Args:
        server: Server state dictionary
        
    Raises:
        RuntimeError: If server is already running
    """
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
    """
    Stop WebSocket server and disconnect all clients.
    
    Args:
        server: Server state dictionary
    """
    if not server['running']:
        return
        
    server['running'] = False
    
    # Disconnect all clients
    for client in server['clients'].copy():
        try:
            await client['websocket'].close()
        except websockets.exceptions.WebSocketException:
            pass
        client['connected'] = False
        server['clients'].remove(client)
    
    # Cancel server task
    if server['task']:
        server['task'].cancel()
        try:
            await server['task']
        except asyncio.CancelledError:
            pass

async def broadcast_message(server: Server, msg_type: str, payload: dict) -> None:
    """
    Broadcast message to all connected clients.
    
    Args:
        server: Server state dictionary
        msg_type: Message type identifier
        payload: Message payload dictionary
    """
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
            await client['websocket'].send(message)
        except websockets.exceptions.WebSocketException:
            # Remove disconnected client
            client['connected'] = False
            server['clients'].remove(client)
            try:
                await client['websocket'].close()
            except websockets.exceptions.WebSocketException:
                pass
