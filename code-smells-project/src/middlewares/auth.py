"""Middleware de autenticação e autorização por JWT.

O legado não tinha nenhuma proteção: qualquer visitante anônimo listava usuários,
alterava preços e lia pedidos de terceiros.
"""

from functools import wraps

from flask import current_app, g, request

from src.repositories import usuario_repository
from src.utils.errors import ForbiddenError, UnauthorizedError
from src.utils.security import decodificar_token

_PREFIXO_BEARER = "bearer "


def _extrair_token() -> str:
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.lower().startswith(_PREFIXO_BEARER):
        raise UnauthorizedError("Envie o token no header 'Authorization: Bearer <token>'")
    token = cabecalho[len(_PREFIXO_BEARER):].strip()
    if not token:
        raise UnauthorizedError("Token ausente")
    return token


def carregar_usuario_autenticado():
    """Valida o token e devolve o usuário atual, cacheado na request."""
    if "usuario_atual" in g:
        return g.usuario_atual

    payload = decodificar_token(_extrair_token(), current_app.config["SETTINGS"].secret_key)
    try:
        usuario_id = int(payload.get("sub", ""))
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Token inválido") from exc

    # Recarregamos do banco em vez de confiar no payload: contas removidas ou
    # rebaixadas perdem o acesso imediatamente, sem esperar o token expirar.
    usuario = usuario_repository.buscar_por_id(usuario_id)
    if usuario is None:
        raise UnauthorizedError("Token inválido")

    g.usuario_atual = usuario
    return usuario


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        carregar_usuario_autenticado()
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = carregar_usuario_autenticado()
        if not usuario.is_admin:
            raise ForbiddenError("Esta operação exige privilégios de administrador")
        return func(*args, **kwargs)

    return wrapper
