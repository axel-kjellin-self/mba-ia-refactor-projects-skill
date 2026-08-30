"""Acesso a dados de pedidos.

A listagem resolve o N+1 do legado: uma query para os pedidos da página e uma
query com JOIN para todos os itens dessa página, montadas em memória.
No legado eram 1 + N + (N × M) queries.
"""

from src.config.database import get_db
from src.models.pedido import ItemPedido, Pedido

_COLUNAS = "id, usuario_id, status, total, criado_em"


def _montar_pedidos(rows) -> list:
    pedidos = [
        Pedido(
            id=row["id"],
            usuario_id=row["usuario_id"],
            status=row["status"],
            total=row["total"],
            criado_em=row["criado_em"],
        )
        for row in rows
    ]
    if not pedidos:
        return []

    ids = tuple(pedido.id for pedido in pedidos)
    placeholders = ",".join("?" * len(ids))
    itens_rows = get_db().execute(
        f"""
        SELECT ip.pedido_id,
               ip.produto_id,
               COALESCE(p.nome, 'Desconhecido') AS produto_nome,
               ip.quantidade,
               ip.preco_unitario
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        ORDER BY ip.id
        """,
        ids,
    ).fetchall()

    por_pedido: dict = {}
    for row in itens_rows:
        por_pedido.setdefault(row["pedido_id"], []).append(
            ItemPedido(
                produto_id=row["produto_id"],
                produto_nome=row["produto_nome"],
                quantidade=row["quantidade"],
                preco_unitario=row["preco_unitario"],
            )
        )

    for pedido in pedidos:
        pedido.itens = por_pedido.get(pedido.id, [])
    return pedidos


def listar(limite: int, offset: int) -> list:
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM pedidos ORDER BY id DESC LIMIT ? OFFSET ?",
        (limite, offset),
    ).fetchall()
    return _montar_pedidos(rows)


def listar_por_usuario(usuario_id: int, limite: int, offset: int) -> list:
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM pedidos WHERE usuario_id = ? "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (usuario_id, limite, offset),
    ).fetchall()
    return _montar_pedidos(rows)


def contar() -> int:
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def contar_por_usuario(usuario_id: int) -> int:
    return get_db().execute(
        "SELECT COUNT(*) FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    ).fetchone()[0]


def buscar_por_id(pedido_id: int) -> Pedido | None:
    row = get_db().execute(
        f"SELECT {_COLUNAS} FROM pedidos WHERE id = ?", (pedido_id,)
    ).fetchone()
    if row is None:
        return None
    return _montar_pedidos([row])[0]


def inserir(conexao, usuario_id: int, status: str, total: float) -> int:
    cursor = conexao.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, status, total),
    )
    return cursor.lastrowid


def inserir_itens(conexao, pedido_id: int, itens) -> None:
    conexao.executemany(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
        "VALUES (?, ?, ?, ?)",
        [
            (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
            for item in itens
        ],
    )


def atualizar_status(conexao, pedido_id: int, novo_status: str) -> bool:
    cursor = conexao.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
    )
    return cursor.rowcount > 0


def listar_itens_brutos(pedido_id: int) -> list:
    rows = get_db().execute(
        "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?",
        (pedido_id,),
    ).fetchall()
    return [dict(row) for row in rows]
