from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class UnauthorizedError(AppError):
    """Unauthorized access error"""
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    """Forbidden access error"""
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403)


def register_error_handlers(app):
    """Register all error handlers with Flask app"""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle custom application errors"""
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors"""
        return jsonify({'errors': error.messages}), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle ValueError (business logic errors)"""
        logger.warning(f"ValueError: {error}")
        return jsonify({'error': str(error)}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors"""
        logger.error(f"Database integrity error: {error}")
        from src.config.database import db
        db.session.rollback()
        return jsonify({'error': 'Database constraint violation'}), 400

    @app.errorhandler(DataError)
    def handle_data_error(error):
        """Handle database data errors"""
        logger.error(f"Database data error: {error}")
        from src.config.database import db
        db.session.rollback()
        return jsonify({'error': 'Invalid data format'}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}", exc_info=True)
        from src.config.database import db
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle all other unexpected errors"""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        from src.config.database import db
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
