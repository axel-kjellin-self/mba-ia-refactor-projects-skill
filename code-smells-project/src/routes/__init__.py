"""Registro central de rotas."""

from flask import Blueprint, Flask, jsonify

from src.routes.pedido_routes import pedido_bp
from src.routes.produto_routes import produto_bp
from src.routes.relatorio_routes import relatorio_bp
from src.routes.usuario_routes import usuario_bp

raiz_bp = Blueprint("raiz", __name__)


@raiz_bp.get("/")
def index():
    """Descoberta da API."""
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def register_routes(app: Flask) -> None:
    """Registra todos os blueprints da aplicação."""
    app.register_blueprint(raiz_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)
