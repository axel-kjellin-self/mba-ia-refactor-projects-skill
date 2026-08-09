"""
Loja Virtual API - Refactored MVC Architecture

This is the main entry point for the Flask application.
Uses Application Factory pattern for better testability and configuration.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from src.config.settings import get_config
from src.config.database import init_db
from src.routes import register_routes
from src.middlewares.error_handler import register_error_handlers
from src.middlewares.logging_middleware import setup_logging
from src.controllers.pedido_controller import PedidoController


def create_app(config_name=None):
    """
    Application factory pattern

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    config = get_config(config_name)

    # Validate configuration
    config.validate()

    # Apply configuration
    app.config.from_object(config)

    # Initialize extensions
    CORS(app)

    # Initialize database
    init_db(app)

    # Setup logging
    setup_logging(app)

    # Register error handlers
    register_error_handlers(app)

    # Register routes
    register_routes(app)

    # Health check route
    @app.route('/health', methods=['GET'])
    def health():
        return PedidoController.health_check()

    # Welcome route
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'mensagem': 'Bem-vindo à API da Loja - Versão Refatorada',
            'versao': '2.0.0',
            'endpoints': {
                'login': 'POST /login',
                'usuarios': '/usuarios',
                'produtos': '/produtos',
                'pedidos': '/pedidos',
                'relatorios': '/relatorios/vendas',
                'health': '/health'
            },
            'documentacao': 'API refatorada seguindo padrão MVC + Service Layer'
        })

    return app


if __name__ == '__main__':
    # Create application
    app = create_app()

    # Get configuration
    print("=" * 60)
    print("SERVIDOR INICIADO - Versão Refatorada MVC")
    print(f"Ambiente: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Rodando em http://{app.config['HOST']}:{app.config['PORT']}")
    print("=" * 60)
    print("\nIMPORTANTE: Configure o arquivo .env antes de usar em produção!")
    print("Use .env.example como template\n")

    # Run application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
