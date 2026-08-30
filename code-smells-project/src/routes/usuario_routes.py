"""Rotas de usuários e autenticação.

Cadastro e login são públicos; a listagem completa é exclusiva de
administradores e a consulta individual exige ser o próprio usuário.
"""

from flask import Blueprint

from src.controllers.usuario_controller import UsuarioController
from src.middlewares.auth import require_admin, require_self_or_admin

usuario_bp = Blueprint("usuarios", __name__)
_controller = UsuarioController()

usuario_bp.post("/usuarios")(_controller.criar)
usuario_bp.post("/login")(_controller.login)

usuario_bp.get("/usuarios")(require_admin(_controller.listar))
usuario_bp.get("/usuarios/<int:usuario_id>")(
    require_self_or_admin("usuario_id")(_controller.buscar)
)
