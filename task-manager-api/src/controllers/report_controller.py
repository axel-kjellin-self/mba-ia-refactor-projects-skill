"""Controller de relatórios."""
from flask import jsonify

from src.config.constants import UserRole
from src.middlewares.auth import require_self_or_role
from src.services.report_service import ReportService


class ReportController:
    def __init__(self, report_service: ReportService | None = None) -> None:
        self.report_service = report_service or ReportService()

    def summary(self):
        """GET /reports/summary — restrito a admin/manager pela rota."""
        return jsonify(self.report_service.summary()), 200

    def user_report(self, user_id: int):
        """GET /reports/user/<user_id> — próprio usuário ou admin/manager."""
        require_self_or_role(user_id, UserRole.ADMIN.value, UserRole.MANAGER.value)
        return jsonify(self.report_service.user_report(user_id)), 200
