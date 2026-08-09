from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os

from src.config.settings import config, Config
from src.config.database import init_db
from src.routes import register_routes
from src.middlewares.error_handler import register_error_handlers
from src.middlewares.logging_middleware import setup_logging


def create_app(config_name=None):
    """
    Application factory pattern

    Args:
        config_name: Configuration to use ('development', 'production', 'test')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please create a .env file based on .env.example")
        raise

    # Initialize extensions
    CORS(app)
    init_db(app)

    # Setup logging
    setup_logging(app)

    # Register error handlers
    register_error_handlers(app)

    # Register routes
    register_routes(app)

    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name
        })

    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Task Manager API - Refactored',
            'version': '2.0',
            'documentation': '/health for status'
        })

    return app


if __name__ == '__main__':
    app = create_app()

    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
