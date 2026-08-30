"""Validação de payloads de usuário e de login."""

from src.config.constants import (
    NOME_USUARIO_TAMANHO_MAXIMO,
    NOME_USUARIO_TAMANHO_MINIMO,
    SENHA_TAMANHO_MAXIMO,
    SENHA_TAMANHO_MINIMO,
)
from src.schemas import validators
from src.utils.errors import ValidationError


def validar_novo_usuario(dados) -> dict:
    dados = validators.exigir_dict(dados)
    return {
        "nome": validators.texto(
            dados,
            "nome",
            minimo=NOME_USUARIO_TAMANHO_MINIMO,
            maximo=NOME_USUARIO_TAMANHO_MAXIMO,
        ),
        "email": validators.email(dados),
        "senha": _validar_forca_da_senha(
            validators.texto(dados, "senha", minimo=1, maximo=SENHA_TAMANHO_MAXIMO)
        ),
    }


def validar_login(dados) -> dict:
    dados = validators.exigir_dict(dados)
    return {
        "email": validators.texto(dados, "email", minimo=3, maximo=254).lower(),
        "senha": validators.texto(dados, "senha", minimo=1, maximo=SENHA_TAMANHO_MAXIMO),
    }


def _validar_forca_da_senha(senha: str) -> str:
    """Exige comprimento mínimo e três classes de caracteres.

    O legado aceitava qualquer senha não vazia — daí "123456" no banco.
    """
    if len(senha) < SENHA_TAMANHO_MINIMO:
        raise ValidationError(
            f"A senha deve ter ao menos {SENHA_TAMANHO_MINIMO} caracteres"
        )

    classes = sum(
        [
            any(c.islower() for c in senha),
            any(c.isupper() for c in senha),
            any(c.isdigit() for c in senha),
            any(not c.isalnum() for c in senha),
        ]
    )
    if classes < 3:
        raise ValidationError(
            "A senha deve combinar ao menos três entre: minúsculas, maiúsculas, "
            "números e símbolos"
        )
    return senha
