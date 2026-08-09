from flask import Blueprint
from src.controllers.task_controller import TaskController
from src.middlewares.auth import require_auth

# Create blueprint
task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# Instantiate controller
task_controller = TaskController()

# Routes
task_bp.route('/', methods=['GET'])(task_controller.get_all)
task_bp.route('/<int:task_id>', methods=['GET'])(task_controller.get_by_id)
task_bp.route('/', methods=['POST'])(task_controller.create)
task_bp.route('/<int:task_id>', methods=['PUT'])(task_controller.update)
task_bp.route('/<int:task_id>', methods=['DELETE'])(task_controller.delete)
task_bp.route('/search', methods=['GET'])(task_controller.search)
task_bp.route('/stats', methods=['GET'])(task_controller.get_stats)
