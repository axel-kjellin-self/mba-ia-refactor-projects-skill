from flask import Flask
from src.routes.auth_routes import auth_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.produto_routes import produto_bp
from src.routes.pedido_routes import pedido_bp
from src.routes.relatorio_routes import relatorio_bp


def register_routes(app: Flask):
    """Register all application blueprints"""

    # Authentication routes
    app.register_blueprint(auth_bp)

    # Resource routes
    app.register_blueprint(usuario_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)

    print("✓ Routes registered")
