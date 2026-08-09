from functools import wraps
from flask import request, jsonify
import jwt
from src.config.settings import Config
from src.models.user import User
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require JWT authentication

    Usage:
        @require_auth
        def my_endpoint():
            user_id = request.current_user_id
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401

        try:
            # Remove "Bearer " prefix
            token = auth_header.replace('Bearer ', '')

            # Decode JWT
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )

            # Inject user info into request context
            request.current_user_id = payload['user_id']
            request.current_user_email = payload.get('email')
            request.current_user_role = payload.get('role', 'user')

        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return jsonify({'error': 'Token expired'}), 401

        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return jsonify({'error': 'Invalid token'}), 401

        except Exception as e:
            logger.error(f"Auth error: {e}", exc_info=True)
            return jsonify({'error': 'Authentication error'}), 401

        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    """
    Decorator to require admin role

    Usage:
        @require_admin
        def admin_only_endpoint():
            ...
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if request.current_user_role != 'admin':
            logger.warning(f"Forbidden access attempt by user {request.current_user_id}")
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)

    return decorated


def require_owner_or_admin(f):
    """
    Decorator to require user is owner or admin

    Usage:
        @require_owner_or_admin
        def endpoint(user_id):
            # user_id must match current_user_id or user must be admin
            ...
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        user_id = kwargs.get('user_id')

        # Check if user is admin or owner
        if request.current_user_id != user_id and request.current_user_role != 'admin':
            logger.warning(f"Forbidden access attempt by user {request.current_user_id} to user {user_id}")
            return jsonify({'error': 'Forbidden'}), 403

        return f(*args, **kwargs)

    return decorated
