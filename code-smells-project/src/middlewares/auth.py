from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from src.config.settings import get_config
from src.models.usuario import Usuario


config = get_config()


def gerar_token(usuario):
    """
    Generate JWT token for authenticated user

    Args:
        usuario: Usuario instance

    Returns:
        JWT token string
    """
    payload = {
        'user_id': usuario.id,
        'email': usuario.email,
        'tipo': usuario.tipo,
        'exp': datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm='HS256'
    )

    return token


def require_auth(f):
    """
    Decorator to require JWT authentication

    Sets request.current_user_id and request.is_admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '')

        if not token:
            return jsonify({'error': 'Token de autenticação não fornecido'}), 401

        # Remove "Bearer " prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )

            # Set user info in request context
            request.current_user_id = payload['user_id']
            request.is_admin = payload.get('tipo') == 'admin'

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    """
    Decorator to require admin role

    Must be used after @require_auth
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if not request.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores'}), 403

        return f(*args, **kwargs)

    return decorated


def require_owner_or_admin(f):
    """
    Decorator to require user to be owner of resource or admin

    Must be used after @require_auth
    Expects user_id parameter in route
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        user_id = kwargs.get('user_id') or kwargs.get('usuario_id')

        # Allow if user is admin or accessing their own resource
        if request.is_admin or request.current_user_id == user_id:
            return f(*args, **kwargs)

        return jsonify({'error': 'Acesso negado'}), 403

    return decorated
