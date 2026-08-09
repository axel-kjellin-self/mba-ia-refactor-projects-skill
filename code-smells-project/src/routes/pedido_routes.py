from flask import Blueprint
from src.controllers.pedido_controller import PedidoController
from src.middlewares.auth import require_auth, require_admin

# Create blueprint
pedido_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

# Controllers
pedido_controller = PedidoController()

# Routes

# POST /pedidos - Create new order
pedido_bp.route('/', methods=['POST'])(pedido_controller.criar_pedido)

# GET /pedidos - List all orders (should be admin only in production)
pedido_bp.route('/', methods=['GET'])(pedido_controller.listar_todos_pedidos)

# GET /pedidos/usuario/<id> - List user orders
pedido_bp.route('/usuario/<int:usuario_id>', methods=['GET'])(
    pedido_controller.listar_pedidos_usuario
)

# PUT /pedidos/<id>/status - Update order status
pedido_bp.route('/<int:pedido_id>/status', methods=['PUT'])(
    pedido_controller.atualizar_status_pedido
)
