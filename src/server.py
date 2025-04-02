#!/usr/bin/env python3
"""
Server entry point.
Runs the WebSocket server with game and lobby functionality.
"""
import asyncio
from typing import NoReturn
from config import get_server_config
from socket_adapter.server_adapter import create_server, start_server, stop_server

async def run_server() -> NoReturn:
    """Run WebSocket server."""
    config = get_server_config()
    server = None

    try:
        # Create and start server
        print(f"Starting server on port {config['port']}...")
        server = create_server(config['port'])  # No await needed - just creates state
        await start_server(server)  # await needed - actually starts server

        print("Server running. Press Ctrl+C to stop.")

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except (asyncio.CancelledError, KeyboardInterrupt) as e:
        print("\nShutting down server...")
        if server:
            await stop_server(server)
        print("Server stopped.")
        if isinstance(e, asyncio.CancelledError):
            raise
    
    except Exception as e:
        print(f"Error running server: {e}")
        if server:
            await stop_server(server)
        raise

def main() -> NoReturn:
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
