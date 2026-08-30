"""Autenticação: cadastro, login e emissão de token."""

import logging
import sqlite3

from src.config.constants import TIPO_CLIENTE
from src.repositories import usuario_repository
from src.utils.errors import ConflictError, UnauthorizedError
from src.utils.security import gerar_token, hash_senha, verificar_senha

logger = logging.getLogger(__name__)

# Hash descartável usado quando o email não existe, para que o tempo de resposta
# do login não revele se a conta está cadastrada (timing oracle).
_HASH_DUMMY = hash_senha("senha-inexistente-para-comparacao-constante")


def registrar(dados_validados: dict) -> dict:
    try:
        usuario_id = usuario_repository.inserir(
            nome=dados_validados["nome"],
            email=dados_validados["email"],
            senha_hash=hash_senha(dados_validados["senha"]),
            tipo=TIPO_CLIENTE,
        )
    except sqlite3.IntegrityError as exc:
        # A constraint UNIQUE(email) é a fonte da verdade: checar antes abriria
        # uma janela de corrida entre a checagem e o insert.
        raise ConflictError("Email já cadastrado") from exc

    logger.info("Usuário criado", extra={"usuario_id": usuario_id})
    return {"id": usuario_id}


def autenticar(dados_validados: dict, settings) -> dict:
    usuario = usuario_repository.buscar_por_email(dados_validados["email"])
    hash_para_comparar = usuario.senha_hash if usuario else _HASH_DUMMY
    senha_confere = verificar_senha(dados_validados["senha"], hash_para_comparar)

    if usuario is None or not senha_confere:
        logger.warning("Tentativa de login falhou")
        # Mensagem genérica: não revela se o erro foi no email ou na senha.
        raise UnauthorizedError("Email ou senha inválidos")

    token = gerar_token(
        usuario_id=usuario.id,
        tipo=usuario.tipo,
        secret_key=settings.secret_key,
        expiracao_minutos=settings.jwt_expiration_minutes,
    )
    logger.info("Login bem-sucedido", extra={"usuario_id": usuario.id})
    return {
        "token": token,
        "expira_em_minutos": settings.jwt_expiration_minutes,
        "usuario": usuario.to_dict(),
    }
