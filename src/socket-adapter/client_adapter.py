#!/usr/bin/env python3
"""
Client adapter for WebSocket communication.
Handles connection management and message processing.
"""
import json
import asyncio
import websockets
from typing import Dict, Any, Callable
from datetime import datetime, timedelta

# Type aliases
Connection = Dict[str, Any]
MessageHandler = Callable[[Dict[str, Any]], None]
MessageHandlers = Dict[str, MessageHandler]

# Constants
HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 2 * HEARTBEAT_INTERVAL  # 2 missed heartbeats

def create_connection_state(websocket: websockets.WebSocketClientProtocol) -> Connection:
    """Create immutable connection state dictionary."""
    return {
        'websocket': websocket,
        'connected': True,
        'last_heartbeat': datetime.now(),
        'handlers': {},
        'task': None
    }

async def send_heartbeat(connection: Connection) -> None:
    """Send heartbeat message to server."""
    try:
        await connection['websocket'].send(json.dumps({
            'type': 'ping',
            'payload': {},
            'timestamp': datetime.now().timestamp()
        }))
    except websockets.exceptions.WebSocketException:
        pass  # Connection handler will deal with failures

async def handle_messages(connection: Connection, handlers: MessageHandlers) -> None:
    """Handle incoming messages from server."""
    while connection['connected']:
        try:
            message = await connection['websocket'].recv()
            data = json.loads(message)
            
            if data['type'] == 'pong':
                connection['last_heartbeat'] = datetime.now()
                continue
                
            if data['type'] in handlers:
                handlers[data['type']](data['payload'])
                
        except websockets.exceptions.WebSocketException:
            connection['connected'] = False
            break
        except json.JSONDecodeError:
            continue  # Skip invalid messages

async def heartbeat_loop(connection: Connection) -> None:
    """Maintain heartbeat with server."""
    while connection['connected']:
        await send_heartbeat(connection)
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        
        # Check for stale connection
        if datetime.now() - connection['last_heartbeat'] > timedelta(seconds=HEARTBEAT_TIMEOUT):
            connection['connected'] = False
            break

# Public API

async def connect(url: str) -> Connection:
    """
    Establish WebSocket connection to server.
    
    Args:
        url: WebSocket server URL
        
    Returns:
        Connection state dictionary
        
    Raises:
        ConnectionError: If connection fails
    """
    try:
        websocket = await websockets.connect(url)
        return create_connection_state(websocket)
    except Exception as e:
        raise ConnectionError(f"Failed to connect: {str(e)}")

async def disconnect(connection: Connection) -> None:
    """
    Close WebSocket connection gracefully.
    
    Args:
        connection: Connection state dictionary
    """
    if not connection['connected']:
        return
        
    try:
        await connection['websocket'].send(json.dumps({
            'type': 'disconnect',
            'payload': {},
            'timestamp': datetime.now().timestamp()
        }))
        await connection['websocket'].close()
    except websockets.exceptions.WebSocketException:
        pass  # Already disconnected
    finally:
        connection['connected'] = False
        if connection['task']:
            connection['task'].cancel()

async def send_message(connection: Connection, msg_type: str, payload: dict) -> None:
    """
    Send message to server.
    
    Args:
        connection: Connection state dictionary
        msg_type: Message type identifier
        payload: Message payload dictionary
        
    Raises:
        ConnectionError: If connection is closed
    """
    if not connection['connected']:
        raise ConnectionError("Connection is closed")
        
    try:
        await connection['websocket'].send(json.dumps({
            'type': msg_type,
            'payload': payload,
            'timestamp': datetime.now().timestamp()
        }))
    except websockets.exceptions.WebSocketException as e:
        connection['connected'] = False
        raise ConnectionError(f"Failed to send message: {str(e)}")

async def start_message_handler(connection: Connection, message_handlers: MessageHandlers) -> None:
    """
    Start message handling and heartbeat loops.
    
    Args:
        connection: Connection state dictionary
        message_handlers: Dictionary mapping message types to handler functions
    """
    if not connection['connected']:
        raise ConnectionError("Connection is closed")
        
    # Create tasks for message handling and heartbeat
    message_task = asyncio.create_task(handle_messages(connection, message_handlers))
    heartbeat_task = asyncio.create_task(heartbeat_loop(connection))
    
    # Combine tasks
    connection['task'] = asyncio.gather(message_task, heartbeat_task)
    
    try:
        await connection['task']
    except asyncio.CancelledError:
        pass  # Normal cancellation during disconnect
    finally:
        connection['connected'] = False
