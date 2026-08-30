"""Rota de autenticação — pública por natureza."""
from flask import Blueprint

from src.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
controller = AuthController()

auth_bp.add_url_rule('/login', 'login', controller.login, methods=['POST'])
