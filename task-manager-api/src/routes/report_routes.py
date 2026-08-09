from flask import Blueprint
from src.controllers.report_controller import ReportController, CategoryController

# Create blueprint
report_bp = Blueprint('reports', __name__)

# Instantiate controllers
report_controller = ReportController()
category_controller = CategoryController()

# Report routes
report_bp.route('/reports/summary', methods=['GET'])(report_controller.get_summary)
report_bp.route('/reports/user/<int:user_id>', methods=['GET'])(report_controller.get_user_report)

# Category routes
report_bp.route('/categories', methods=['GET'])(category_controller.get_all)
report_bp.route('/categories', methods=['POST'])(category_controller.create)
report_bp.route('/categories/<int:cat_id>', methods=['PUT'])(category_controller.update)
report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])(category_controller.delete)
