from flask import Blueprint
from src.controllers.usuario_controller import UsuarioController
from src.middlewares.auth import require_auth, require_owner_or_admin

# Create blueprint
usuario_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Controllers
usuario_controller = UsuarioController()

# Routes

# GET /usuarios - List all users (should be protected in production)
usuario_bp.route('/', methods=['GET'])(usuario_controller.listar_usuarios)

# GET /usuarios/<id> - Get user by ID
usuario_bp.route('/<int:usuario_id>', methods=['GET'])(usuario_controller.buscar_usuario)

# POST /usuarios - Create new user
usuario_bp.route('/', methods=['POST'])(usuario_controller.criar_usuario)
