#!/usr/bin/env python3
"""
Client adapter for WebSocket communication.
Handles connection management and message processing.
"""
import json
import asyncio
import websockets
from typing import Dict, Any, Callable, Tuple
from datetime import datetime
from websockets.client import WebSocketClientProtocol

# Type aliases
MessageHandler = Callable[[Dict[str, Any]], None]
MessageHandlers = Dict[str, MessageHandler]
ClientState = Tuple[WebSocketClientProtocol, datetime, bool]  # (websocket, last_heartbeat, connected)

# Pure functions for state management

def create_client_state(websocket: WebSocketClientProtocol) -> ClientState:
    """Create immutable client state tuple."""
    return (websocket, datetime.now(), True)

def disconnect_client(client: ClientState) -> ClientState:
    """Create new client state marked as disconnected."""
    return (client[0], client[1], False)

# Message handling

async def send_message(client: ClientState, msg_type: str, payload: dict) -> None:
    """Send message to server."""
    if not client[2]:  # not connected
        raise ConnectionError("Connection is closed")
        
    try:
        message = json.dumps({
            'type': msg_type,
            'payload': payload,
            'timestamp': datetime.now().timestamp()
        })
        await client[0].send(message)
    except websockets.exceptions.WebSocketException as e:
        raise ConnectionError(f"Failed to send message: {str(e)}")

async def handle_messages(client: ClientState, handlers: MessageHandlers) -> None:
    """Handle incoming messages from server."""
    while client[2]:  # while connected
        try:
            message = await client[0].recv()
            
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                print(f"Failed to parse message: {e}")
                continue
                
            if data['type'] in handlers:
                try:
                    if 'payload' in data:
                        handlers[data['type']](data['payload'])
                    else:
                        print(f"No payload in message: {data}")
                except Exception as e:
                    print(f"Error handling {data['type']}: {e}")
            else:
                print(f"No handler for message type: {data['type']}")
                
        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

# Public API

async def connect(url: str) -> ClientState:
    """
    Establish WebSocket connection to server.
    
    Args:
        url: WebSocket server URL
        
    Returns:
        ClientState tuple
        
    Raises:
        ConnectionError: If connection fails
    """
    try:
        websocket = await websockets.connect(
            url,
            ping_interval=20,    # Send ping every 20 seconds
            ping_timeout=60      # Wait 60 seconds for pong response
        )
        return create_client_state(websocket)
    except Exception as e:
        raise ConnectionError(f"Failed to connect: {str(e)}")

async def disconnect(client: ClientState) -> None:
    """Close WebSocket connection gracefully."""
    if not client[2]:  # not connected
        return
        
    try:
        await send_message(client, 'disconnect', {})
        await client[0].close()
    except (ConnectionError, websockets.exceptions.WebSocketException):
        pass  # Already disconnected

async def start_message_handler(client: ClientState, message_handlers: MessageHandlers) -> None:
    """Start message handling loop."""
    if not client[2]:  # not connected
        raise ConnectionError("Connection is closed")
    
    # Request initial lobby status
    await send_message(client, 'get_lobby_status', {})
    
    # Start message handling
    await handle_messages(client, message_handlers)
