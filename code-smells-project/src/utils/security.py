"""Primitivas de segurança: hash de senha e emissão/verificação de JWT.

Substitui o armazenamento e a comparação de senhas em texto plano que existiam
em ``models.py``.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from src.config.settings import Config

_BCRYPT_ROUNDS = 12


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt (com salt próprio) de uma senha."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(_BCRYPT_ROUNDS)).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Compara a senha informada com o hash armazenado, em tempo constante."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
    except (ValueError, TypeError):
        # Hash corrompido ou em formato legado: trata como falha de autenticação.
        return False


def gerar_token(usuario_id: int, tipo: str) -> str:
    """Emite um JWT de acesso para o usuário."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "tipo": tipo,
        "iat": agora,
        "exp": agora + timedelta(seconds=Config.JWT_EXPIRES_SECONDS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def decodificar_token(token: str) -> dict[str, Any]:
    """Valida assinatura e expiração, devolvendo o payload.

    Raises:
        jwt.InvalidTokenError: token inválido, expirado ou adulterado.
    """
    return jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
