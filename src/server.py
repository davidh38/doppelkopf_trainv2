"""
Server entry point.
Runs the game server with configured adapters.
"""
import asyncio
from typing import NoReturn
from src.config import get_server_config
from src.wiring.service_wiring import create_game_environment, create_lobby_environment

async def run_server() -> NoReturn:
    """Run game and lobby servers."""
    config = get_server_config()
    
    try:
        # Create game and lobby services
        print(f"Starting game server on port {config['game_port']}...")
        game_service = await create_game_environment(config['game_port'])
        
        print(f"Starting lobby server on port {config['lobby_port']}...")
        lobby_service = await create_lobby_environment(config['lobby_port'])
        
        # Start services
        await asyncio.gather(
            game_service['server'].start(),
            lobby_service['server'].start()
        )
        
        print("Servers running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        if 'game_service' in locals():
            await game_service['server'].stop()
        if 'lobby_service' in locals():
            await lobby_service['server'].stop()
        print("Servers stopped.")
    
    except Exception as e:
        print(f"Error running servers: {e}")
        if 'game_service' in locals():
            await game_service['server'].stop()
        if 'lobby_service' in locals():
            await lobby_service['server'].stop()
        raise

def main() -> NoReturn:
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
