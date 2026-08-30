"""Tratamento de erros centralizado.

Substitui os 11 `except:` nus espalhados pelas rotas, que engoliam a exceção,
perdiam o stack trace e devolviam 500 mesmo para erros de validação.
"""
import logging

from flask import Flask, jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from src.config.database import db
from src.utils.exceptions import DomainError

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(error: MarshmallowValidationError):
        """Falha de schema → 400 com os campos problemáticos."""
        return jsonify({'error': 'Dados inválidos', 'details': error.messages}), 400

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError):
        """Erro de negócio → status declarado pela própria exceção."""
        payload = {'error': error.message}
        if error.details:
            payload['details'] = error.details
        return jsonify(payload), error.status_code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        """Violação de constraint → 409, não 500."""
        db.session.rollback()
        logger.warning('Violação de integridade: %s', error.orig)
        return jsonify({'error': 'Violação de integridade dos dados'}), 409

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error: SQLAlchemyError):
        db.session.rollback()
        logger.error('Erro de banco de dados', exc_info=error)
        return jsonify({'error': 'Erro ao acessar o banco de dados'}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Rede de segurança: loga o stack trace e nunca vaza detalhes internos."""
        db.session.rollback()
        logger.error('Erro não tratado', exc_info=error)
        return jsonify({'error': 'Erro interno do servidor'}), 500
