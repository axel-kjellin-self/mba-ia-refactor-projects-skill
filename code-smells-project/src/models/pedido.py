"""Entidades Pedido e ItemPedido."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ItemPedido:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float

    @property
    def subtotal(self) -> float:
        return round(self.quantidade * self.preco_unitario, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "produto_id": self.produto_id,
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "subtotal": self.subtotal,
        }


@dataclass(frozen=True, slots=True)
class Pedido:
    id: int
    usuario_id: int
    status: str
    total: float
    criado_em: str
    itens: list[ItemPedido] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "status": self.status,
            "total": self.total,
            "criado_em": self.criado_em,
            "itens": [item.to_dict() for item in self.itens],
        }


@dataclass(frozen=True, slots=True)
class ItemPedidoInput:
    """Item solicitado pelo cliente, já validado."""

    produto_id: int
    quantidade: int
