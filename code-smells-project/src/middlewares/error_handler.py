from flask import jsonify
from sqlalchemy.exc import IntegrityError, DataError
from src.config.database import db
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for application errors"""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    """Resource not found error"""

    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)


class ValidationError(AppError):
    """Validation error"""

    def __init__(self, message):
        super().__init__(message, 400)


class UnauthorizedError(AppError):
    """Unauthorized access error"""

    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    """Forbidden access error"""

    def __init__(self, message="Acesso proibido"):
        super().__init__(message, 403)


def register_error_handlers(app):
    """Register all error handlers with Flask app"""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle custom application errors"""
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        """Handle not found errors"""
        return jsonify({'error': error.message}), 404

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        return jsonify({'error': error.message}), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle ValueError (business logic errors)"""
        logger.warning(f"ValueError: {error}")
        return jsonify({'error': str(error)}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors"""
        logger.error(f"Database integrity error: {error}")
        db.session.rollback()
        return jsonify({
            'error': 'Violação de integridade do banco de dados'
        }), 400

    @app.errorhandler(DataError)
    def handle_data_error(error):
        """Handle database data errors"""
        logger.error(f"Database data error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Erro de dados no banco'}), 400

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 Not Found"""
        return jsonify({'error': 'Endpoint não encontrado'}), 404

    @app.errorhandler(405)
    def handle_405(error):
        """Handle 405 Method Not Allowed"""
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal server error: {error}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Erro inesperado'}), 500
