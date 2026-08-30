"""Controller HTTP de relatórios e health check."""

from flask import jsonify

from src.controllers import http
from src.services.relatorio_service import RelatorioService


class RelatorioController:
    def __init__(self, servico: RelatorioService | None = None) -> None:
        self.servico = servico or RelatorioService()

    def vendas(self):
        """GET /relatorios/vendas — restrito a administradores."""
        return http.ok(self.servico.vendas())

    def health(self):
        """GET /health — endpoint público, sem dados sensíveis."""
        resultado = self.servico.health()
        status_http = 200 if resultado["status"] == "ok" else 503
        return jsonify(resultado), status_http
