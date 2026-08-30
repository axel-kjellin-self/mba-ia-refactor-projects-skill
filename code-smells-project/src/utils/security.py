"""Hashing de senhas (bcrypt) e emissão/verificação de tokens JWT."""

import datetime as dt

import bcrypt
import jwt

from src.utils.errors import UnauthorizedError

_ALGORITMO_JWT = "HS256"
# bcrypt trunca a entrada em 72 bytes; rejeitamos antes para não aceitar
# silenciosamente senhas longas cujo sufixo é ignorado.
_TAMANHO_MAXIMO_BCRYPT_BYTES = 72


def hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > _TAMANHO_MAXIMO_BCRYPT_BYTES:
        raise ValueError("Senha excede o limite de 72 bytes suportado pelo bcrypt")
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        # Hash malformado no banco (ex.: registro herdado em texto plano).
        return False


def gerar_token(usuario_id: int, tipo: str, secret_key: str, expiracao_minutos: int) -> str:
    agora = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "tipo": tipo,
        "iat": agora,
        "exp": agora + dt.timedelta(minutes=expiracao_minutos),
    }
    return jwt.encode(payload, secret_key, algorithm=_ALGORITMO_JWT)


def decodificar_token(token: str, secret_key: str) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms=[_ALGORITMO_JWT])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Token inválido") from exc
