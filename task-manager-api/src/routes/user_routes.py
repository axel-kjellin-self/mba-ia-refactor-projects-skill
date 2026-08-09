from flask import Blueprint
from src.controllers.user_controller import UserController
from src.middlewares.auth import require_auth, require_owner_or_admin

# Create blueprint
user_bp = Blueprint('users', __name__)

# Instantiate controller
user_controller = UserController()

# Public routes
user_bp.route('/login', methods=['POST'])(user_controller.login)

# User management routes
user_bp.route('/users', methods=['GET'])(user_controller.get_all)
user_bp.route('/users/<int:user_id>', methods=['GET'])(user_controller.get_by_id)
user_bp.route('/users', methods=['POST'])(user_controller.create)
user_bp.route('/users/<int:user_id>', methods=['PUT'])(user_controller.update)
user_bp.route('/users/<int:user_id>', methods=['DELETE'])(user_controller.delete)
user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])(user_controller.get_user_tasks)
