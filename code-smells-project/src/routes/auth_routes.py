from flask import Blueprint
from src.controllers.usuario_controller import UsuarioController

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Controllers
usuario_controller = UsuarioController()

# Routes

# POST /login - Authenticate user
auth_bp.route('/login', methods=['POST'])(usuario_controller.login)
