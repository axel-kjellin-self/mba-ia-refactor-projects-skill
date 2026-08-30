"""Acesso a dados de produtos. Somente SQL — nenhuma regra de negócio aqui."""

from src.config.database import get_db
from src.models.produto import Produto

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def listar(limite: int, offset: int) -> list:
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos ORDER BY id LIMIT ? OFFSET ?",
        (limite, offset),
    ).fetchall()
    return [Produto.from_row(row) for row in rows]


def contar() -> int:
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]


def buscar_por_id(produto_id: int) -> Produto | None:
    row = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    return Produto.from_row(row) if row else None


def pesquisar(
    termo: str | None,
    categoria: str | None,
    preco_min: float | None,
    preco_max: float | None,
    limite: int,
    offset: int,
) -> list:
    """Filtro dinâmico montado com placeholders — nunca com concatenação."""
    clausulas = ["1=1"]
    parametros: list = []

    if termo:
        clausulas.append("(nome LIKE ? ESCAPE '\\' OR descricao LIKE ? ESCAPE '\\')")
        padrao = f"%{_escapar_like(termo)}%"
        parametros.extend([padrao, padrao])
    if categoria:
        clausulas.append("categoria = ?")
        parametros.append(categoria)
    if preco_min is not None:
        clausulas.append("preco >= ?")
        parametros.append(preco_min)
    if preco_max is not None:
        clausulas.append("preco <= ?")
        parametros.append(preco_max)

    where = " AND ".join(clausulas)
    parametros.extend([limite, offset])
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE {where} ORDER BY id LIMIT ? OFFSET ?",
        tuple(parametros),
    ).fetchall()
    return [Produto.from_row(row) for row in rows]


def _escapar_like(termo: str) -> str:
    """Neutraliza os curingas do LIKE para que o termo seja tratado como literal."""
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def inserir(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
    conexao = get_db()
    cursor = conexao.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conexao.commit()
    return cursor.lastrowid


def atualizar(
    produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str
) -> bool:
    conexao = get_db()
    cursor = conexao.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
        "categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conexao.commit()
    return cursor.rowcount > 0


def deletar(produto_id: int) -> bool:
    conexao = get_db()
    cursor = conexao.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conexao.commit()
    return cursor.rowcount > 0


def buscar_varios_por_id(produto_ids) -> dict:
    """Carrega vários produtos numa query só (usado na criação de pedido)."""
    ids = tuple(dict.fromkeys(produto_ids))
    if not ids:
        return {}
    placeholders = ",".join("?" * len(ids))
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE id IN ({placeholders})", ids
    ).fetchall()
    return {row["id"]: Produto.from_row(row) for row in rows}


def debitar_estoque(conexao, produto_id: int, quantidade: int) -> bool:
    """Baixa o estoque de forma atômica.

    A condição ``estoque >= ?`` faz a verificação e o débito na mesma instrução:
    se outra transação consumiu o saldo no meio do caminho, ``rowcount`` é 0 e o
    chamador aborta — o legado checava e debitava em passos separados.
    """
    cursor = conexao.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount > 0


def creditar_estoque(conexao, produto_id: int, quantidade: int) -> None:
    """Devolve unidades ao estoque (usado no cancelamento de pedido)."""
    conexao.execute(
        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
        (quantidade, produto_id),
    )
