"""Rotas de relatórios, health check e índice da API."""

from flask import Blueprint, jsonify

from src.controllers import relatorio_controller
from src.middlewares.auth import admin_required

relatorio_bp = Blueprint("relatorios", __name__)

relatorio_bp.get("/relatorios/vendas")(admin_required(relatorio_controller.relatorio_vendas))
relatorio_bp.get("/health")(relatorio_controller.health_check)


@relatorio_bp.get("/")
def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "busca_produtos": "/produtos/busca",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "perfil": "/me",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
            "autenticacao": "Bearer token JWT obtido em POST /login",
        }
    )
