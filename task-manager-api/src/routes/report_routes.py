"""Rotas de relatórios."""
from flask import Blueprint

from src.config.constants import UserRole
from src.controllers.report_controller import ReportController
from src.middlewares.auth import require_auth, require_role

report_bp = Blueprint('reports', __name__, url_prefix='/reports')
controller = ReportController()

report_bp.add_url_rule(
    '/summary',
    'summary',
    require_role(UserRole.ADMIN.value, UserRole.MANAGER.value)(controller.summary),
    methods=['GET'],
)
report_bp.add_url_rule(
    '/user/<int:user_id>', 'user_report', require_auth(controller.user_report), methods=['GET']
)
