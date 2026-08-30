"""Controllers de relatórios e health check."""

from flask import jsonify

from src.controllers.http import sucesso
from src.services import relatorio_service


def relatorio_vendas():
    return sucesso(relatorio_service.gerar_relatorio_de_vendas())


def health_check():
    # Resposta enxuta e sem secrets: o legado devolvia SECRET_KEY, db_path e o
    # flag de debug para qualquer chamador anônimo.
    return jsonify(relatorio_service.status_da_aplicacao()), 200
