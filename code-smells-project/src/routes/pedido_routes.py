"""Rotas de pedidos. Todas exigem autenticação."""

from flask import Blueprint

from src.controllers.pedido_controller import PedidoController
from src.middlewares.auth import require_admin, require_auth, require_self_or_admin

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")
_controller = PedidoController()

pedido_bp.post("")(require_auth(_controller.criar))
pedido_bp.get("/<int:pedido_id>")(require_auth(_controller.buscar))

pedido_bp.get("")(require_admin(_controller.listar_todos))
pedido_bp.put("/<int:pedido_id>/status")(require_admin(_controller.atualizar_status))

pedido_bp.get("/usuario/<int:usuario_id>")(
    require_self_or_admin("usuario_id")(_controller.listar_por_usuario)
)
