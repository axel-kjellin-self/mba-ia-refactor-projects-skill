"""Registro central dos blueprints."""

from src.routes.pedido_routes import pedido_bp
from src.routes.produto_routes import produto_bp
from src.routes.relatorio_routes import relatorio_bp
from src.routes.usuario_routes import auth_bp, usuario_bp

BLUEPRINTS = (produto_bp, usuario_bp, auth_bp, pedido_bp, relatorio_bp)


def register_blueprints(app) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
