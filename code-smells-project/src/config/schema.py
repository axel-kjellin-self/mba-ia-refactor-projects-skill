"""Definição do schema do banco e carga de dados de exemplo.

Antes esse código rodava como efeito colateral de ``get_db()``, em toda
inicialização de conexão. Agora é uma etapa explícita de bootstrap.

Diferenças em relação ao schema original: colunas obrigatórias marcadas como
NOT NULL, e-mail único, foreign keys declaradas, CHECKs de domínio e índices
nas colunas usadas em junção.
"""

import logging
import sqlite3

from src.config.constants import Categoria, StatusPedido, TipoUsuario
from src.config.settings import Config
from src.utils.security import hash_senha

logger = logging.getLogger(__name__)

_CATEGORIAS_SQL = ", ".join(f"'{c}'" for c in Categoria.VALIDAS)
_STATUS_SQL = ", ".join(f"'{s}'" for s in StatusPedido.VALIDOS)
_TIPOS_SQL = ", ".join(f"'{t}'" for t in TipoUsuario.VALIDOS)

DDL: tuple[str, ...] = (
    f"""
    CREATE TABLE IF NOT EXISTS produtos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        nome       TEXT    NOT NULL,
        descricao  TEXT    NOT NULL DEFAULT '',
        preco      REAL    NOT NULL CHECK (preco >= 0),
        estoque    INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
        categoria  TEXT    NOT NULL CHECK (categoria IN ({_CATEGORIAS_SQL})),
        ativo      INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
        criado_em  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS usuarios (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        nome       TEXT    NOT NULL,
        email      TEXT    NOT NULL UNIQUE,
        senha_hash TEXT    NOT NULL,
        tipo       TEXT    NOT NULL DEFAULT '{TipoUsuario.CLIENTE}'
                           CHECK (tipo IN ({_TIPOS_SQL})),
        criado_em  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS pedidos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
        status     TEXT    NOT NULL DEFAULT '{StatusPedido.PENDENTE}'
                           CHECK (status IN ({_STATUS_SQL})),
        total      REAL    NOT NULL CHECK (total >= 0),
        criado_em  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id      INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
        produto_id     INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
        quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
        preco_unitario REAL    NOT NULL CHECK (preco_unitario >= 0)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos(usuario_id)",
    "CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status)",
    "CREATE INDEX IF NOT EXISTS idx_itens_pedido ON itens_pedido(pedido_id)",
    "CREATE INDEX IF NOT EXISTS idx_itens_produto ON itens_pedido(produto_id)",
    "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
)

PRODUTOS_EXEMPLO: tuple[tuple[str, str, float, int, str], ...] = (
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
)


def criar_schema(conexao: sqlite3.Connection) -> None:
    """Cria tabelas e índices caso ainda não existam."""
    for statement in DDL:
        conexao.execute(statement)


def popular_dados_exemplo(conexao: sqlite3.Connection) -> None:
    """Insere catálogo e usuário admin de exemplo, se o banco estiver vazio.

    A senha do admin vem de ``SEED_ADMIN_PASSWORD``; sem ela, nenhum usuário é
    criado — o código original gravava ``admin123`` em texto plano.
    """
    if conexao.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        conexao.executemany(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            PRODUTOS_EXEMPLO,
        )
        logger.info("Catálogo de exemplo carregado (%d produtos)", len(PRODUTOS_EXEMPLO))

    if conexao.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        if not Config.SEED_ADMIN_PASSWORD:
            logger.warning(
                "SEED_ADMIN_PASSWORD não definida: nenhum usuário admin foi criado. "
                "Defina a variável e reinicie, ou cadastre o admin manualmente."
            )
            return

        conexao.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
            (
                "Admin",
                "admin@loja.com",
                hash_senha(Config.SEED_ADMIN_PASSWORD),
                TipoUsuario.ADMIN,
            ),
        )
        logger.info("Usuário admin de exemplo criado (admin@loja.com)")


def init_db(conexao: sqlite3.Connection) -> None:
    """Bootstrap completo do banco."""
    criar_schema(conexao)
    if Config.SEED_DATA:
        popular_dados_exemplo(conexao)
