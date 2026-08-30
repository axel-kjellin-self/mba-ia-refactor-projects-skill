"""Criação do schema e seed inicial.

No código legado o schema era criado como efeito colateral do ``get_db()``, o que
misturava infraestrutura com acesso a dados. Aqui a inicialização é explícita:
``flask init-db`` ou ``init_database(app)`` no boot em desenvolvimento.
"""

import logging

from src.config.constants import TIPO_ADMIN
from src.config.database import get_db
from src.utils.security import hash_senha

logger = logging.getLogger(__name__)

# FOREIGN KEYs, UNIQUE e NOT NULL ausentes no schema legado; índices adicionados
# nas colunas usadas em filtro/join.
_DDL = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL DEFAULT '',
        preco REAL NOT NULL CHECK (preco >= 0),
        estoque INTEGER NOT NULL CHECK (estoque >= 0),
        categoria TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'cliente',
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
        status TEXT NOT NULL DEFAULT 'pendente',
        total REAL NOT NULL CHECK (total >= 0),
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
        produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
    "CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos(usuario_id)",
    "CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status)",
    "CREATE INDEX IF NOT EXISTS idx_itens_pedido ON itens_pedido(pedido_id)",
)

_PRODUTOS_EXEMPLO = (
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


def criar_schema() -> None:
    conexao = get_db()
    for ddl in _DDL:
        conexao.execute(ddl)
    conexao.commit()


def popular_dados_iniciais(settings) -> None:
    """Insere catálogo de exemplo e, se configurado, o usuário admin.

    O admin só é criado quando SEED_ADMIN_EMAIL/PASSWORD estão definidos e o
    ambiente não é produção — o legado criava "admin@loja.com / admin123" sempre.
    """
    conexao = get_db()

    if conexao.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        conexao.executemany(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            _PRODUTOS_EXEMPLO,
        )
        conexao.commit()
        logger.info("Catálogo de exemplo inserido (%d produtos)", len(_PRODUTOS_EXEMPLO))

    if settings.is_production:
        return
    if not settings.seed_admin_email or not settings.seed_admin_password:
        return

    ja_existe = conexao.execute(
        "SELECT 1 FROM usuarios WHERE email = ?", (settings.seed_admin_email,)
    ).fetchone()
    if ja_existe:
        return

    conexao.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (
            "Admin",
            settings.seed_admin_email,
            hash_senha(settings.seed_admin_password),
            TIPO_ADMIN,
        ),
    )
    conexao.commit()
    logger.info("Usuário admin de desenvolvimento criado: %s", settings.seed_admin_email)


def init_database(app) -> None:
    with app.app_context():
        criar_schema()
        popular_dados_iniciais(app.config["SETTINGS"])
