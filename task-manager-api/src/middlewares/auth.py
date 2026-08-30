"""Middleware de autenticação e autorização.

Antes o projeto não tinha nenhuma verificação: os 19 endpoints, incluindo os
três DELETE, eram públicos.
"""
from functools import wraps
from typing import Callable

from flask import g, request

from src.config.constants import UserRole
from src.services.auth_service import AuthService
from src.utils.exceptions import AuthenticationError, AuthorizationError

_auth_service = AuthService()


def _extract_token() -> str:
    header = request.headers.get('Authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        raise AuthenticationError('Token de autenticação ausente')
    return token.strip()


def require_auth(func: Callable) -> Callable:
    """Exige um JWT válido. Popula `g.current_user_id` e `g.current_user_role`."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = _auth_service.decode_token(_extract_token())
        g.current_user_id = payload['user_id']
        g.current_user_role = payload.get('role', UserRole.USER.value)
        return func(*args, **kwargs)

    return wrapper


def require_role(*roles: str) -> Callable:
    """Exige um JWT válido cujo `role` esteja entre os informados."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @require_auth
        def wrapper(*args, **kwargs):
            if g.current_user_role not in roles:
                raise AuthorizationError('Permissão insuficiente para esta operação')
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_self_or_role(user_id: int, *roles: str) -> None:
    """Bloqueia IDOR: o dono do recurso passa, os demais precisam de um role.

    Chamada de dentro do controller, onde o `user_id` do path já é conhecido.
    """
    if g.current_user_id == user_id:
        return
    if g.current_user_role in roles:
        return
    raise AuthorizationError('Você só pode acessar os seus próprios dados')
