"""Acesso a dados de produtos. Todas as queries são parametrizadas."""

import sqlite3

from src.config.database import get_db
from src.models.produto import Produto

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


class ProdutoRepository:
    """Repositório de produtos."""

    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao = conexao

    @property
    def db(self) -> sqlite3.Connection:
        return self._conexao if self._conexao is not None else get_db()

    def listar(self, limite: int, offset: int = 0) -> list[Produto]:
        rows = self.db.execute(
            f"SELECT {_COLUNAS} FROM produtos ORDER BY id LIMIT ? OFFSET ?",
            (limite, offset),
        ).fetchall()
        return [Produto.from_row(row) for row in rows]

    def contar(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        row = self.db.execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return Produto.from_row(row) if row else None

    def buscar_varios_por_id(self, ids: list[int]) -> dict[int, Produto]:
        """Carrega vários produtos numa única query, indexados por id.

        Usado na criação de pedidos para evitar uma query por item.
        """
        if not ids:
            return {}
        placeholders = ", ".join("?" for _ in ids)
        rows = self.db.execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id IN ({placeholders})", tuple(ids)
        ).fetchall()
        return {row["id"]: Produto.from_row(row) for row in rows}

    def pesquisar(
        self,
        termo: str | None = None,
        categoria: str | None = None,
        preco_min: float | None = None,
        preco_max: float | None = None,
        limite: int = 50,
        offset: int = 0,
    ) -> list[Produto]:
        """Busca com filtros opcionais.

        As cláusulas são montadas dinamicamente, mas cada valor entra como
        placeholder — inclusive o termo do LIKE, cujos curingas são aplicados ao
        parâmetro e não à string SQL.
        """
        clausulas: list[str] = []
        params: list[object] = []

        if termo:
            clausulas.append("(nome LIKE ? ESCAPE '\\' OR descricao LIKE ? ESCAPE '\\')")
            padrao = f"%{_escapar_like(termo)}%"
            params.extend([padrao, padrao])
        if categoria:
            clausulas.append("categoria = ?")
            params.append(categoria)
        if preco_min is not None:
            clausulas.append("preco >= ?")
            params.append(preco_min)
        if preco_max is not None:
            clausulas.append("preco <= ?")
            params.append(preco_max)

        where = f"WHERE {' AND '.join(clausulas)}" if clausulas else ""
        params.extend([limite, offset])

        rows = self.db.execute(
            f"SELECT {_COLUNAS} FROM produtos {where} ORDER BY id LIMIT ? OFFSET ?",
            tuple(params),
        ).fetchall()
        return [Produto.from_row(row) for row in rows]

    def criar(
        self, nome: str, descricao: str, preco: float, estoque: int, categoria: str
    ) -> int:
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid

    def atualizar(
        self,
        produto_id: int,
        nome: str,
        descricao: str,
        preco: float,
        estoque: int,
        categoria: str,
    ) -> bool:
        cursor = self.db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
            "categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        return cursor.rowcount > 0

    def deletar(self, produto_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        return cursor.rowcount > 0

    def baixar_estoque(self, produto_id: int, quantidade: int) -> bool:
        """Decrementa o estoque de forma condicional.

        A checagem ``estoque >= ?`` acontece dentro do UPDATE: se outra
        transação consumiu o estoque no intervalo entre a validação e a escrita,
        nenhuma linha é afetada e o chamador detecta a corrida.
        """
        cursor = self.db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
            (quantidade, produto_id, quantidade),
        )
        return cursor.rowcount > 0

    def repor_estoque(self, produto_id: int, quantidade: int) -> None:
        self.db.execute(
            "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
            (quantidade, produto_id),
        )


def _escapar_like(termo: str) -> str:
    """Neutraliza os curingas do LIKE para que sejam tratados como literais."""
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
