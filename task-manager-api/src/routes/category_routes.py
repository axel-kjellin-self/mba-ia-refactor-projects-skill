"""Rotas de categorias.

Separadas de `report_routes` — antes o CRUD de categorias estava indevidamente
dentro do blueprint de relatórios.
"""
from flask import Blueprint

from src.config.constants import UserRole
from src.controllers.category_controller import CategoryController
from src.middlewares.auth import require_auth, require_role

category_bp = Blueprint('categories', __name__, url_prefix='/categories')
controller = CategoryController()

PRIVILEGED = (UserRole.ADMIN.value, UserRole.MANAGER.value)

category_bp.add_url_rule('', 'list', require_auth(controller.list), methods=['GET'])
category_bp.add_url_rule(
    '', 'create', require_role(*PRIVILEGED)(controller.create), methods=['POST']
)
category_bp.add_url_rule(
    '/<int:category_id>',
    'update',
    require_role(*PRIVILEGED)(controller.update),
    methods=['PUT'],
)
category_bp.add_url_rule(
    '/<int:category_id>',
    'delete',
    require_role(UserRole.ADMIN.value)(controller.delete),
    methods=['DELETE'],
)
