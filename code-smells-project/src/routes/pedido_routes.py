"""Rotas de pedido."""

from flask import Blueprint

from src.controllers import pedido_controller
from src.middlewares.auth import admin_required, login_required

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

pedido_bp.post("")(login_required(pedido_controller.criar_pedido))
pedido_bp.get("")(admin_required(pedido_controller.listar_todos_pedidos))
pedido_bp.get("/usuario/<int:usuario_id>")(
    login_required(pedido_controller.listar_pedidos_usuario)
)
pedido_bp.put("/<int:pedido_id>/status")(
    admin_required(pedido_controller.atualizar_status_pedido)
)
