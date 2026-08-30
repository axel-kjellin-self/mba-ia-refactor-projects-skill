"""Acesso a dados de usuários.

O hash da senha só é carregado quando explicitamente solicitado
(``buscar_por_email_com_senha``), usado apenas no fluxo de login.
"""

import sqlite3

from src.config.database import get_db
from src.models.usuario import Usuario

_COLUNAS = "id, nome, email, tipo, criado_em"


class UsuarioRepository:
    """Repositório de usuários."""

    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao = conexao

    @property
    def db(self) -> sqlite3.Connection:
        return self._conexao if self._conexao is not None else get_db()

    def listar(self, limite: int, offset: int = 0) -> list[Usuario]:
        rows = self.db.execute(
            f"SELECT {_COLUNAS} FROM usuarios ORDER BY id LIMIT ? OFFSET ?",
            (limite, offset),
        ).fetchall()
        return [Usuario.from_row(row) for row in rows]

    def contar(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        row = self.db.execute(
            f"SELECT {_COLUNAS} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return Usuario.from_row(row) if row else None

    def buscar_por_email_com_senha(self, email: str) -> Usuario | None:
        """Carrega o usuário incluindo o hash, exclusivamente para autenticação."""
        row = self.db.execute(
            f"SELECT {_COLUNAS}, senha_hash FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        return Usuario.from_row(row, com_senha=True) if row else None

    def email_existe(self, email: str) -> bool:
        row = self.db.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone()
        return row is not None

    def criar(self, nome: str, email: str, senha_hash: str, tipo: str) -> int:
        cursor = self.db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        return cursor.lastrowid
