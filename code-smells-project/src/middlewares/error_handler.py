"""Tratamento centralizado de erros.

Substitui os 15 blocos ``try/except Exception`` que devolviam ``str(e)`` ao
cliente com status 500 — vazando mensagens internas e impedindo o cliente de
distinguir erro de entrada de falha do servidor.
"""

import logging
import sqlite3

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from src.utils.errors import AppError, ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """Registra os handlers globais de erro."""

    @app.errorhandler(ValidationError)
    def _validacao(erro: ValidationError):
        corpo = {"erro": erro.message, "sucesso": False}
        if erro.fields:
            corpo["campos"] = erro.fields
        return jsonify(corpo), erro.status_code

    @app.errorhandler(AppError)
    def _erro_aplicacao(erro: AppError):
        return jsonify({"erro": erro.message, "sucesso": False}), erro.status_code

    @app.errorhandler(HTTPException)
    def _erro_http(erro: HTTPException):
        # Cobre 404 de rota inexistente, 405 de método errado e 400 de JSON malformado.
        return jsonify({"erro": erro.description, "sucesso": False}), erro.code

    @app.errorhandler(sqlite3.IntegrityError)
    def _integridade(erro: sqlite3.IntegrityError):
        logger.warning("Violação de integridade: %s", erro)
        return (
            jsonify({"erro": "Operação viola uma restrição de integridade.", "sucesso": False}),
            409,
        )

    @app.errorhandler(sqlite3.Error)
    def _erro_banco(erro: sqlite3.Error):
        logger.error("Erro de banco de dados", exc_info=erro)
        return jsonify({"erro": "Erro interno do servidor.", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def _inesperado(erro: Exception):
        # O detalhe vai para o log; o cliente recebe apenas uma mensagem genérica.
        logger.exception("Erro não tratado", exc_info=erro)
        return jsonify({"erro": "Erro interno do servidor.", "sucesso": False}), 500
