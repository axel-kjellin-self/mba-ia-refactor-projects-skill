"""Schemas de entrada para usuários e autenticação."""

from dataclasses import dataclass
from typing import Any

from src.config.constants import RegrasValidacao
from src.schemas import validators


@dataclass(frozen=True, slots=True)
class UsuarioInput:
    nome: str
    email: str
    senha: str


@dataclass(frozen=True, slots=True)
class LoginInput:
    email: str
    senha: str


def carregar_usuario(dados: Any) -> UsuarioInput:
    """Valida o cadastro de usuário, incluindo formato de e-mail e força da senha."""
    dados = validators.exigir_objeto(dados)

    return UsuarioInput(
        nome=validators.texto(
            dados,
            "nome",
            minimo=RegrasValidacao.NOME_USUARIO_MIN,
            maximo=RegrasValidacao.NOME_USUARIO_MAX,
        ),
        email=validators.email(dados, "email", maximo=RegrasValidacao.EMAIL_MAX),
        senha=validators.texto(
            dados,
            "senha",
            minimo=RegrasValidacao.SENHA_MIN,
            maximo=RegrasValidacao.SENHA_MAX,
        ),
    )


def carregar_login(dados: Any) -> LoginInput:
    """Valida as credenciais de login.

    Não aplica regras de força de senha: senhas cadastradas antes de uma
    mudança de política ainda precisam conseguir autenticar.
    """
    dados = validators.exigir_objeto(dados)

    return LoginInput(
        email=validators.email(dados, "email", maximo=RegrasValidacao.EMAIL_MAX),
        senha=validators.texto(dados, "senha", minimo=1, maximo=RegrasValidacao.SENHA_MAX),
    )
