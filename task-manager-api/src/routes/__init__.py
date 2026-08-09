from flask import Flask
from src.routes.task_routes import task_bp
from src.routes.user_routes import user_bp
from src.routes.report_routes import report_bp


def register_routes(app: Flask):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

