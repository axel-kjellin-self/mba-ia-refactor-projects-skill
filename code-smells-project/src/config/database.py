"""Gerenciamento de conexão com o SQLite.

Substitui a conexão global compartilhada entre threads (``check_same_thread=False``)
por uma conexão por request, ancorada no contexto de aplicação do Flask.
"""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from flask import Flask, g

from src.config.settings import Config


def _conectar() -> sqlite3.Connection:
    conexao = sqlite3.connect(Config.DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    # Integridade referencial precisa ser habilitada por conexão no SQLite.
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def get_db() -> sqlite3.Connection:
    """Devolve a conexão do request atual, criando-a sob demanda."""
    if "db" not in g:
        g.db = _conectar()
    return g.db


def close_db(_exception: BaseException | None = None) -> None:
    """Fecha a conexão ao fim do request."""
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


@contextmanager
def transacao() -> Iterator[sqlite3.Connection]:
    """Executa um bloco de operações atomicamente.

    Faz commit ao final e rollback em caso de exceção — ausente na criação de
    pedidos do código original, que podia deixar itens e estoque inconsistentes.
    """
    conexao = get_db()
    try:
        yield conexao
    except Exception:
        conexao.rollback()
        raise
    else:
        conexao.commit()


@contextmanager
def conexao_avulsa() -> Iterator[sqlite3.Connection]:
    """Conexão fora do ciclo de request (inicialização, scripts, testes)."""
    conexao = _conectar()
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def init_app(app: Flask) -> None:
    """Registra o teardown que fecha a conexão ao término de cada request."""
    app.teardown_appcontext(close_db)
