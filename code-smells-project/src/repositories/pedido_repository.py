"""Acesso a dados de pedidos.

A montagem de pedidos com itens usa uma única query com JOIN, substituindo o
laço aninhado que gerava 1 + N + N*M queries no código original.
"""

import sqlite3

from src.config.database import get_db
from src.models.pedido import ItemPedido, Pedido

_SELECT_PEDIDOS_COM_ITENS = """
    SELECT
        p.id            AS pedido_id,
        p.usuario_id    AS usuario_id,
        p.status        AS status,
        p.total         AS total,
        p.criado_em     AS criado_em,
        ip.produto_id   AS produto_id,
        ip.quantidade   AS quantidade,
        ip.preco_unitario AS preco_unitario,
        pr.nome         AS produto_nome
    FROM ({subquery}) AS p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr     ON pr.id = ip.produto_id
    ORDER BY p.id, ip.id
"""


class PedidoRepository:
    """Repositório de pedidos."""

    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao = conexao

    @property
    def db(self) -> sqlite3.Connection:
        return self._conexao if self._conexao is not None else get_db()

    def listar(self, limite: int, offset: int = 0) -> list[Pedido]:
        subquery = "SELECT * FROM pedidos ORDER BY id LIMIT ? OFFSET ?"
        rows = self.db.execute(
            _SELECT_PEDIDOS_COM_ITENS.format(subquery=subquery), (limite, offset)
        ).fetchall()
        return _agrupar_pedidos(rows)

    def listar_por_usuario(self, usuario_id: int, limite: int, offset: int = 0) -> list[Pedido]:
        subquery = "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id LIMIT ? OFFSET ?"
        rows = self.db.execute(
            _SELECT_PEDIDOS_COM_ITENS.format(subquery=subquery),
            (usuario_id, limite, offset),
        ).fetchall()
        return _agrupar_pedidos(rows)

    def buscar_por_id(self, pedido_id: int) -> Pedido | None:
        subquery = "SELECT * FROM pedidos WHERE id = ?"
        rows = self.db.execute(
            _SELECT_PEDIDOS_COM_ITENS.format(subquery=subquery), (pedido_id,)
        ).fetchall()
        pedidos = _agrupar_pedidos(rows)
        return pedidos[0] if pedidos else None

    def contar(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    def criar(self, usuario_id: int, status: str, total: float) -> int:
        cursor = self.db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        return cursor.lastrowid

    def adicionar_item(
        self, pedido_id: int, produto_id: int, quantidade: int, preco_unitario: float
    ) -> None:
        self.db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario),
        )

    def atualizar_status(self, pedido_id: int, status: str) -> bool:
        cursor = self.db.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id)
        )
        return cursor.rowcount > 0


def _agrupar_pedidos(rows: list[sqlite3.Row]) -> list[Pedido]:
    """Converte o resultado achatado do JOIN em pedidos com seus itens.

    Preserva a ordem de ``ORDER BY p.id``.
    """
    agrupados: dict[int, dict] = {}

    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in agrupados:
            agrupados[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }

        # LEFT JOIN devolve produto_id nulo para pedidos sem itens.
        if row["produto_id"] is not None:
            agrupados[pedido_id]["itens"].append(
                ItemPedido(
                    produto_id=row["produto_id"],
                    produto_nome=row["produto_nome"] or "Produto removido",
                    quantidade=row["quantidade"],
                    preco_unitario=row["preco_unitario"],
                )
            )

    return [Pedido(**dados) for dados in agrupados.values()]
