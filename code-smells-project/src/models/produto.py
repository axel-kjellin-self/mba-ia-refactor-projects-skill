"""Entidade Produto."""

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Produto:
    id: int
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str
    ativo: bool
    criado_em: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Produto":
        return cls(
            id=row["id"],
            nome=row["nome"],
            descricao=row["descricao"],
            preco=row["preco"],
            estoque=row["estoque"],
            categoria=row["categoria"],
            ativo=bool(row["ativo"]),
            criado_em=row["criado_em"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "estoque": self.estoque,
            "categoria": self.categoria,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }
