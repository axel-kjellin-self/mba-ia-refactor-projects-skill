"""Agregações para relatórios.

As cinco queries sequenciais do relatório de vendas original foram consolidadas
em uma única agregação condicional.
"""

import sqlite3
from dataclasses import dataclass

from src.config.constants import StatusPedido
from src.config.database import get_db


@dataclass(frozen=True, slots=True)
class AgregadoVendas:
    """Números brutos de vendas, sem regra de negócio aplicada."""

    total_pedidos: int
    faturamento_bruto: float
    pendentes: int
    aprovados: int
    cancelados: int


class RelatorioRepository:
    """Repositório de agregações analíticas."""

    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao = conexao

    @property
    def db(self) -> sqlite3.Connection:
        return self._conexao if self._conexao is not None else get_db()

    def agregado_vendas(self) -> AgregadoVendas:
        row = self.db.execute(
            """
            SELECT
                COUNT(*)                                    AS total_pedidos,
                COALESCE(SUM(total), 0)                     AS faturamento,
                COALESCE(SUM(status = ?), 0)                AS pendentes,
                COALESCE(SUM(status = ?), 0)                AS aprovados,
                COALESCE(SUM(status = ?), 0)                AS cancelados
            FROM pedidos
            """,
            (StatusPedido.PENDENTE, StatusPedido.APROVADO, StatusPedido.CANCELADO),
        ).fetchone()

        return AgregadoVendas(
            total_pedidos=row["total_pedidos"],
            faturamento_bruto=row["faturamento"],
            pendentes=row["pendentes"],
            aprovados=row["aprovados"],
            cancelados=row["cancelados"],
        )

    def verificar_conexao(self) -> bool:
        """Ping usado pelo health check."""
        try:
            self.db.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False
