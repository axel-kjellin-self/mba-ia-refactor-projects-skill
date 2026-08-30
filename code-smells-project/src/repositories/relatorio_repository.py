"""Consultas agregadas para relatórios.

O legado disparava 5 queries sequenciais (COUNT, SUM e um COUNT por status);
aqui uma única agregação traz todos os números.
"""

from src.config.database import get_db
from src.config.constants import STATUS_PEDIDO_VALIDOS


def resumo_vendas() -> dict:
    # Uma coluna agregada por status, gerada a partir das constantes de domínio:
    # incluir um novo status não exige tocar nesta query.
    colunas_status = ", ".join(
        f"COALESCE(SUM(status = ?), 0) AS status_{indice}"
        for indice in range(len(STATUS_PEDIDO_VALIDOS))
    )
    row = get_db().execute(
        f"""
        SELECT COUNT(*)                AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               {colunas_status}
        FROM pedidos
        """,
        tuple(STATUS_PEDIDO_VALIDOS),
    ).fetchone()

    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento": row["faturamento"],
        "por_status": {
            status: row[f"status_{indice}"]
            for indice, status in enumerate(STATUS_PEDIDO_VALIDOS)
        },
    }


def contagens_health() -> dict:
    row = get_db().execute(
        """
        SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
               (SELECT COUNT(*) FROM usuarios) AS usuarios,
               (SELECT COUNT(*) FROM pedidos)  AS pedidos
        """
    ).fetchone()
    return {"produtos": row["produtos"], "usuarios": row["usuarios"], "pedidos": row["pedidos"]}
