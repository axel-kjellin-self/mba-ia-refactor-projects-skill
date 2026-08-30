"""Rotas de relatórios e health check."""

from flask import Blueprint

from src.controllers.relatorio_controller import RelatorioController
from src.middlewares.auth import require_admin

relatorio_bp = Blueprint("relatorios", __name__)
_controller = RelatorioController()

relatorio_bp.get("/relatorios/vendas")(require_admin(_controller.vendas))
relatorio_bp.get("/health")(_controller.health)
