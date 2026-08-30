"""Autenticação de usuários."""

import logging

from src.models.usuario import Usuario
from src.repositories.usuario_repository import UsuarioRepository
from src.schemas.usuario_schema import LoginInput
from src.utils.errors import UnauthorizedError
from src.utils.security import gerar_token, hash_senha, verificar_senha

logger = logging.getLogger(__name__)

# Hash descartável usado para igualar o custo do login quando o e-mail não
# existe, evitando que o tempo de resposta revele quais e-mails estão cadastrados.
_HASH_DUMMY = hash_senha("senha-inexistente-para-timing-equalization")


class AuthService:
    def __init__(self, repositorio: UsuarioRepository | None = None) -> None:
        self.repositorio = repositorio or UsuarioRepository()

    def autenticar(self, entrada: LoginInput) -> tuple[str, Usuario]:
        """Valida credenciais e emite um token de acesso.

        Raises:
            UnauthorizedError: credenciais inválidas. A mensagem é genérica de
                propósito — distinguir "e-mail não existe" de "senha errada"
                entrega uma lista de usuários válidos ao atacante.
        """
        usuario = self.repositorio.buscar_por_email_com_senha(entrada.email)

        if usuario is None:
            verificar_senha(entrada.senha, _HASH_DUMMY)
            logger.warning("Tentativa de login para e-mail não cadastrado")
            raise UnauthorizedError("E-mail ou senha inválidos.")

        if not verificar_senha(entrada.senha, usuario.senha_hash):
            logger.warning("Senha incorreta para o usuário %s", usuario.id)
            raise UnauthorizedError("E-mail ou senha inválidos.")

        logger.info("Login bem-sucedido para o usuário %s", usuario.id)
        return gerar_token(usuario.id, usuario.tipo), usuario
