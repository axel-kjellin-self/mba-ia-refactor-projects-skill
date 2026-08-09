from flask import Blueprint
from src.controllers.pedido_controller import PedidoController
from src.middlewares.auth import require_auth, require_admin

# Create blueprint
relatorio_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

# Controllers
pedido_controller = PedidoController()

# Routes

# GET /relatorios/vendas - Sales report (should be admin only in production)
relatorio_bp.route('/vendas', methods=['GET'])(pedido_controller.relatorio_vendas)
