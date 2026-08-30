"""Entidade Usuario.

O hash da senha é mantido fora de ``to_dict()``: nenhuma rota deve ser capaz de
expô-lo acidentalmente, que era o caso de ``GET /usuarios`` no código original.
"""

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from src.config.constants import TipoUsuario


@dataclass(frozen=True, slots=True)
class Usuario:
    id: int
    nome: str
    email: str
    tipo: str
    criado_em: str
    # Preenchido apenas no fluxo de autenticação; nunca serializado.
    senha_hash: str | None = field(default=None, repr=False)

    @property
    def is_admin(self) -> bool:
        return self.tipo == TipoUsuario.ADMIN

    @classmethod
    def from_row(cls, row: sqlite3.Row, *, com_senha: bool = False) -> "Usuario":
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            tipo=row["tipo"],
            criado_em=row["criado_em"],
            senha_hash=row["senha_hash"] if com_senha else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "criado_em": self.criado_em,
        }
