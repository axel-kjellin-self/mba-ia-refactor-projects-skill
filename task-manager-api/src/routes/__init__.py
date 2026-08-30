"""Agregação dos blueprints da aplicação."""
from datetime import datetime

from flask import Blueprint, Flask, jsonify

from src.routes.auth_routes import auth_bp
from src.routes.category_routes import category_bp
from src.routes.report_routes import report_bp
from src.routes.task_routes import task_bp
from src.routes.user_routes import user_bp

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health():
    """Liveness probe. Não expõe configuração nem versões internas."""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@health_bp.route('/')
def index():
    return jsonify({'message': 'Task Manager API', 'version': '2.0'}), 200


def register_routes(app: Flask) -> None:
    for blueprint in (health_bp, auth_bp, user_bp, task_bp, category_bp, report_bp):
        app.register_blueprint(blueprint)
