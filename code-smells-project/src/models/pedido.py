"""Entidades Pedido e ItemPedido."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ItemPedido:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float

    @property
    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario

    def to_dict(self) -> dict:
        return {
            "produto_id": self.produto_id,
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "subtotal": round(self.subtotal, 2),
        }


@dataclass
class Pedido:
    id: int
    usuario_id: int
    status: str
    total: float
    criado_em: str
    itens: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "status": self.status,
            "total": self.total,
            "criado_em": self.criado_em,
            "itens": [item.to_dict() for item in self.itens],
        }
