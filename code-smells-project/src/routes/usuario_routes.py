"""Rotas de usuário e autenticação."""

from flask import Blueprint

from src.controllers import usuario_controller
from src.middlewares.auth import admin_required, login_required

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")
auth_bp = Blueprint("auth", __name__)

# Listar todos os usuários é operação administrativa; a consulta individual
# valida ownership dentro do controller.
usuario_bp.get("")(admin_required(usuario_controller.listar_usuarios))
usuario_bp.get("/<int:usuario_id>")(login_required(usuario_controller.buscar_usuario))
usuario_bp.post("")(usuario_controller.criar_usuario)

auth_bp.post("/login")(usuario_controller.login)
auth_bp.get("/me")(login_required(usuario_controller.perfil))
