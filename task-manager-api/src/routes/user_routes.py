"""Rotas de usuários — apenas URL → controller, com os middlewares aplicados."""
from flask import Blueprint

from src.config.constants import UserRole
from src.controllers.user_controller import UserController
from src.middlewares.auth import require_auth, require_role

user_bp = Blueprint('users', __name__, url_prefix='/users')
controller = UserController()

user_bp.add_url_rule(
    '',
    'list',
    require_role(UserRole.ADMIN.value, UserRole.MANAGER.value)(controller.list),
    methods=['GET'],
)
user_bp.add_url_rule(
    '/<int:user_id>', 'get', require_auth(controller.get), methods=['GET']
)
# Registro público — único endpoint de escrita sem autenticação.
user_bp.add_url_rule('', 'create', controller.create, methods=['POST'])
user_bp.add_url_rule(
    '/<int:user_id>', 'update', require_auth(controller.update), methods=['PUT']
)
user_bp.add_url_rule(
    '/<int:user_id>',
    'delete',
    require_role(UserRole.ADMIN.value)(controller.delete),
    methods=['DELETE'],
)
user_bp.add_url_rule(
    '/<int:user_id>/tasks', 'list_tasks', require_auth(controller.list_tasks), methods=['GET']
)
