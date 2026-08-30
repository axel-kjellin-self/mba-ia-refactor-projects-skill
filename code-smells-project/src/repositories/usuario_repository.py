"""Acesso a dados de usuários."""

from src.config.database import get_db
from src.models.usuario import Usuario

_COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"
_COLUNAS_COM_HASH = "id, nome, email, tipo, criado_em, senha_hash"


def listar(limite: int, offset: int) -> list:
    rows = get_db().execute(
        f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios ORDER BY id LIMIT ? OFFSET ?",
        (limite, offset),
    ).fetchall()
    return [Usuario.from_row(row) for row in rows]


def contar() -> int:
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]


def buscar_por_id(usuario_id: int) -> Usuario | None:
    row = get_db().execute(
        f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return Usuario.from_row(row) if row else None


def buscar_por_email(email: str) -> Usuario | None:
    """Retorna o usuário com o hash — uso restrito ao fluxo de autenticação."""
    row = get_db().execute(
        f"SELECT {_COLUNAS_COM_HASH} FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    return Usuario.from_row(row) if row else None


def existe(usuario_id: int) -> bool:
    return get_db().execute(
        "SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone() is not None


def inserir(nome: str, email: str, senha_hash: str, tipo: str) -> int:
    conexao = get_db()
    cursor = conexao.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    conexao.commit()
    return cursor.lastrowid
