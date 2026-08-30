"""Regras de negócio de usuários."""

import sqlite3

from src.config.constants import TipoUsuario
from src.config.database import transacao
from src.models.usuario import Usuario
from src.repositories.usuario_repository import UsuarioRepository
from src.schemas.usuario_schema import UsuarioInput
from src.utils.errors import ConflictError, NotFoundError
from src.utils.security import hash_senha


class UsuarioService:
    def __init__(self, repositorio: UsuarioRepository | None = None) -> None:
        self.repositorio = repositorio or UsuarioRepository()

    def listar(self, limite: int, offset: int = 0) -> list[Usuario]:
        return self.repositorio.listar(limite, offset)

    def buscar(self, usuario_id: int) -> Usuario:
        usuario = self.repositorio.buscar_por_id(usuario_id)
        if usuario is None:
            raise NotFoundError(f"Usuário {usuario_id} não encontrado.")
        return usuario

    def criar(self, entrada: UsuarioInput) -> Usuario:
        """Cadastra um usuário sempre como cliente.

        O papel nunca vem do payload: aceitar ``tipo`` do cliente permitiria
        auto-promoção a admin.
        """
        if self.repositorio.email_existe(entrada.email):
            raise ConflictError("E-mail já cadastrado.")

        try:
            with transacao():
                usuario_id = self.repositorio.criar(
                    entrada.nome,
                    entrada.email,
                    hash_senha(entrada.senha),
                    TipoUsuario.CLIENTE,
                )
        except sqlite3.IntegrityError as exc:
            # Corrida entre a checagem acima e o INSERT: a constraint UNIQUE decide.
            raise ConflictError("E-mail já cadastrado.") from exc

        return self.buscar(usuario_id)
