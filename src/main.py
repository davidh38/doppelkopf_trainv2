"""
Main entry point for the application.
Determines which frontend to use based on configuration.
"""

from typing import NoReturn
from src.config import get_frontend_type, VALID_FRONTEND_TYPES

def run_terminal_frontend() -> NoReturn:
    """Run the terminal frontend."""
    print("Terminal frontend selected")
    # Terminal frontend implementation will go here
    raise NotImplementedError("Terminal frontend not implemented yet")

def run_web_frontend() -> NoReturn:
    """Run the web frontend."""
    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"
    
    print("Web frontend selected")
    app.run(debug=True)

def main() -> NoReturn:
    """Main entry point."""
    frontend_runners = {
        'terminal': run_terminal_frontend,
        'web': run_web_frontend
    }
    
    frontend_type = get_frontend_type()
    runner = frontend_runners[frontend_type]
    runner()

if __name__ == '__main__':
    main()
