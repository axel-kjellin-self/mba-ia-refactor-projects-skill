"""Rotas de tasks — apenas URL → controller, com os middlewares aplicados."""
from flask import Blueprint

from src.config.constants import UserRole
from src.controllers.task_controller import TaskController
from src.middlewares.auth import require_auth, require_role

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')
controller = TaskController()

task_bp.add_url_rule('', 'list', require_auth(controller.list), methods=['GET'])
task_bp.add_url_rule('/search', 'search', require_auth(controller.search), methods=['GET'])
task_bp.add_url_rule('/stats', 'stats', require_auth(controller.stats), methods=['GET'])
task_bp.add_url_rule(
    '/<int:task_id>', 'get', require_auth(controller.get), methods=['GET']
)
task_bp.add_url_rule('', 'create', require_auth(controller.create), methods=['POST'])
task_bp.add_url_rule(
    '/<int:task_id>', 'update', require_auth(controller.update), methods=['PUT']
)
task_bp.add_url_rule(
    '/<int:task_id>',
    'delete',
    require_role(UserRole.ADMIN.value, UserRole.MANAGER.value)(controller.delete),
    methods=['DELETE'],
)
