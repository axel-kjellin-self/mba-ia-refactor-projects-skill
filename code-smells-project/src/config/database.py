"""Gerenciamento de conexão com o SQLite.

Substitui o singleton global do código legado: cada request tem a própria
conexão, guardada em ``flask.g`` e fechada no teardown do app context. Isso
elimina o compartilhamento de cursors/transações entre threads.
"""

import sqlite3
from contextlib import contextmanager

from flask import current_app, g

_APP_CONFIG_KEY = "DATABASE_PATH"


def _abrir_conexao(caminho: str) -> sqlite3.Connection:
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    # Sem este PRAGMA o SQLite ignora as FOREIGN KEYs declaradas no schema.
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def get_db() -> sqlite3.Connection:
    """Retorna a conexão da request atual, criando-a no primeiro acesso."""
    if "db" not in g:
        g.db = _abrir_conexao(current_app.config[_APP_CONFIG_KEY])
    return g.db


def close_db(_exception=None) -> None:
    """Fecha a conexão da request. Registrado como ``teardown_appcontext``."""
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


@contextmanager
def transaction():
    """Executa um bloco de operações numa transação única.

    ``BEGIN IMMEDIATE`` adquire o lock de escrita já na abertura, o que serializa
    operações concorrentes (ex.: dois pedidos disputando o mesmo estoque).
    """
    conexao = get_db()
    conexao.execute("BEGIN IMMEDIATE")
    try:
        yield conexao
    except Exception:
        conexao.rollback()
        raise
    else:
        conexao.commit()


def init_app(app) -> None:
    """Liga o ciclo de vida da conexão ao ciclo de vida da request."""
    app.teardown_appcontext(close_db)
