"""Entidade Usuário.

``senha_hash`` fica fora de ``to_dict()`` por construção: no legado a serialização
manual incluía o campo ``senha`` e vazava as credenciais em ``GET /usuarios``.
"""

from dataclasses import dataclass, field

from src.config.constants import TIPO_ADMIN


@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str
    email: str
    tipo: str
    criado_em: str
    senha_hash: str = field(default="", repr=False)

    @classmethod
    def from_row(cls, row) -> "Usuario":
        chaves = row.keys()
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            tipo=row["tipo"],
            criado_em=row["criado_em"],
            senha_hash=row["senha_hash"] if "senha_hash" in chaves else "",
        )

    @property
    def is_admin(self) -> bool:
        return self.tipo == TIPO_ADMIN

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "criado_em": self.criado_em,
        }
