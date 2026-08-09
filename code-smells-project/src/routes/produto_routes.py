from flask import Blueprint
from src.controllers.produto_controller import ProdutoController
from src.middlewares.auth import require_auth, require_admin

# Create blueprint
produto_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

# Controllers
produto_controller = ProdutoController()

# Routes

# GET /produtos - List all products
produto_bp.route('/', methods=['GET'])(produto_controller.listar_produtos)

# GET /produtos/busca - Search products
produto_bp.route('/busca', methods=['GET'])(produto_controller.buscar_produtos)

# GET /produtos/<id> - Get product by ID
produto_bp.route('/<int:produto_id>', methods=['GET'])(produto_controller.buscar_produto)

# POST /produtos - Create new product (should be protected in production)
produto_bp.route('/', methods=['POST'])(produto_controller.criar_produto)

# PUT /produtos/<id> - Update product (should be protected in production)
produto_bp.route('/<int:produto_id>', methods=['PUT'])(produto_controller.atualizar_produto)

# DELETE /produtos/<id> - Delete product (should be protected in production)
produto_bp.route('/<int:produto_id>', methods=['DELETE'])(produto_controller.deletar_produto)
