"""Tratamento centralizado de erros.

Substitui os 15 blocos ``except Exception`` dos controllers legados, que
devolviam ``str(e)`` ao cliente com status 500 — vazando SQL e detalhes internos,
e impedindo o cliente de distinguir erro de input de falha de servidor.
"""

import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from src.utils.errors import AppError

logger = logging.getLogger(__name__)


def _resposta(mensagem: str, status: int, detalhes: dict | None = None):
    corpo = {"erro": mensagem, "sucesso": False}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def register_error_handlers(app) -> None:
    @app.errorhandler(AppError)
    def _tratar_erro_de_dominio(exc: AppError):
        logger.info("Erro de domínio: %s", exc.mensagem)
        return _resposta(exc.mensagem, exc.status_code, exc.detalhes)

    @app.errorhandler(HTTPException)
    def _tratar_erro_http(exc: HTTPException):
        # Cobre 404 de rota inexistente, 405 de método errado, 400 de JSON malformado.
        return _resposta(exc.description, exc.code or 500)

    @app.errorhandler(Exception)
    def _tratar_erro_inesperado(exc: Exception):
        # Stack trace completo no log, mensagem genérica na resposta.
        logger.exception("Erro não tratado: %s", exc)
        return _resposta("Erro interno do servidor", 500)
