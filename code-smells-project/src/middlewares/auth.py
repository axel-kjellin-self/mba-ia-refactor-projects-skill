"""Autenticação e autorização por JWT.

O código original não tinha nenhuma camada equivalente: todas as rotas eram
públicas, inclusive as destrutivas.
"""

from dataclasses import dataclass
from functools import wraps
from typing import Callable

import jwt
from flask import g, request

from src.config.constants import TipoUsuario
from src.utils.errors import ForbiddenError, UnauthorizedError
from src.utils.security import decodificar_token


@dataclass(frozen=True, slots=True)
class UsuarioAutenticado:
    """Identidade extraída do token, disponível em ``g.usuario``."""

    id: int
    tipo: str

    @property
    def is_admin(self) -> bool:
        return self.tipo == TipoUsuario.ADMIN


def _extrair_token() -> str:
    cabecalho = request.headers.get("Authorization", "")
    prefixo = "Bearer "

    if not cabecalho.startswith(prefixo):
        raise UnauthorizedError("Token de autenticação ausente ou malformado.")

    token = cabecalho[len(prefixo):].strip()
    if not token:
        raise UnauthorizedError("Token de autenticação ausente.")
    return token


def autenticar() -> UsuarioAutenticado:
    """Valida o token do request e devolve a identidade correspondente."""
    token = _extrair_token()

    try:
        payload = decodificar_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expirado.") from None
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Token inválido.") from None

    try:
        usuario_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise UnauthorizedError("Token inválido.") from None

    return UsuarioAutenticado(id=usuario_id, tipo=payload.get("tipo", TipoUsuario.CLIENTE))


def require_auth(funcao: Callable) -> Callable:
    """Exige um token válido e popula ``g.usuario``."""

    @wraps(funcao)
    def wrapper(*args, **kwargs):
        g.usuario = autenticar()
        return funcao(*args, **kwargs)

    return wrapper


def require_admin(funcao: Callable) -> Callable:
    """Exige token válido de um usuário com papel de administrador."""

    @wraps(funcao)
    def wrapper(*args, **kwargs):
        g.usuario = autenticar()
        if not g.usuario.is_admin:
            raise ForbiddenError("Esta operação requer privilégios de administrador.")
        return funcao(*args, **kwargs)

    return wrapper


def require_self_or_admin(param: str = "usuario_id") -> Callable:
    """Permite acesso apenas ao dono do recurso ou a um administrador.

    Fecha o IDOR de ``GET /pedidos/usuario/<id>``, que expunha o histórico de
    compras de qualquer usuário.
    """

    def decorator(funcao: Callable) -> Callable:
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            g.usuario = autenticar()
            alvo = kwargs.get(param)

            if not g.usuario.is_admin and g.usuario.id != alvo:
                raise ForbiddenError("Você só pode acessar os seus próprios dados.")
            return funcao(*args, **kwargs)

        return wrapper

    return decorator


def usuario_atual() -> UsuarioAutenticado:
    """Identidade do request corrente. Só é válida dentro de rotas protegidas."""
    usuario = getattr(g, "usuario", None)
    if usuario is None:
        raise UnauthorizedError("Requisição não autenticada.")
    return usuario
