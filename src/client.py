#!/usr/bin/env python3
"""
Client entry point.
Connects to the WebSocket server and handles game/lobby interactions.
"""
import asyncio
import logging
import sys
from typing import NoReturn, Dict, Any, Optional, TypedDict, Callable
from config import get_client_config
from socket_adapter.client_adapter import connect, disconnect, send_message, start_message_handler
from ui_adapter.terminal.lobby_table_output import run_terminal_ui_adapter
from services.state import get_lobby_state, set_lobby_state

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('client.log')
    ]
)
logger = logging.getLogger('client')

# Type definitions
class ClientState(TypedDict):
    token: Optional[str]

# Pure functions for state management
def create_client_state() -> ClientState:
    """Create initial client state."""
    return {"token": None}

def update_token(state: ClientState, token: str) -> ClientState:
    """Update token in client state."""
    return {**state, "token": token}

# Message handlers
def create_message_handlers(state: ClientState, set_state: Callable[[ClientState], None], websocket_client: Any) -> Dict[str, Any]:
    """Create message handler functions."""
    def handle_lobby_update(payload: Dict[str, Any]) -> None:
        """Update local lobby state."""
        logger.debug("Entering handle_lobby_update")
        logger.debug(f"Lobby update payload: {payload}")
        set_lobby_state(payload)  # Use state module
        logger.debug("State updated")

    def handle_player_connected(payload: Dict[str, Any]) -> None:
        """Handle player connected response."""
        token = payload.get('token')
        if token:
            # Update client state with token
            new_state = update_token(state, token)
            set_state(new_state)
            logger.debug(f"Updated client state with token: {token}")
            # Request lobby refresh immediately after getting token
            asyncio.create_task(send_message(websocket_client, 'get_lobby_status', {}))

    return {
        'lobby_update': handle_lobby_update,
        'player_connected': handle_player_connected,
        'error': lambda data: print(f"\nServer error: {data.get('message', 'Unknown error')}")
    }

# Main client logic

async def run_client() -> NoReturn:
    """Run WebSocket client."""
    config = get_client_config()
    client = None
    
    # Initialize client state
    state = create_client_state()
    
    def set_state(new_state: ClientState) -> None:
        """Update client state."""
        nonlocal state
        state = new_state

    try:
        # Connect to server
        logger.info(f"Connecting to server at {config['server_host']}:{config['port']}...")
        client = await connect(
            f"ws://{config['server_host']}:{config['port']}", 
            ping_timeout=config.get('ping_timeout', None)
        )
        logger.info("Connected to server.")

        # Start message handling with state management
        message_task = asyncio.create_task(
            start_message_handler(client, create_message_handlers(state, set_state, client))
        )

        # Give message handler a chance to initialize
        await asyncio.sleep(0.1)

        # Start terminal UI with WebSocket client and token
        ui_task = asyncio.create_task(
            run_terminal_ui_adapter(client, state["token"])
        )

        # Wait for both tasks to complete
        try:
            await asyncio.gather(message_task, ui_task)
        except asyncio.CancelledError:
            logger.info("Tasks cancelled")
            # Cancel both tasks
            message_task.cancel()
            ui_task.cancel()
            try:
                await message_task
            except asyncio.CancelledError:
                pass
            try:
                await ui_task
            except asyncio.CancelledError:
                pass
            raise

    except (asyncio.CancelledError, KeyboardInterrupt) as e:
        logger.info("Disconnecting from server...")
        if client:
            await disconnect(client)
        logger.info("Disconnected.")
        if isinstance(e, asyncio.CancelledError):
            raise
    
    except Exception as e:
        logger.error(f"Error running client: {e}", exc_info=True)
        if client:
            await disconnect(client)
        raise

def main() -> NoReturn:
    """Main entry point."""
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
