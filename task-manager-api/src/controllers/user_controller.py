"""Controller de usuários. Aplica também as checagens de ownership (anti-IDOR)."""
from flask import jsonify

from src.config.constants import UserRole
from src.controllers.http import json_body
from src.middlewares.auth import require_self_or_role
from src.schemas.task_schema import serialize_tasks
from src.schemas.user_schema import (
    serialize_user,
    user_create_schema,
    user_update_schema,
)
from src.services.user_service import UserService

PRIVILEGED_ROLES = (UserRole.ADMIN.value, UserRole.MANAGER.value)


class UserController:
    def __init__(self, user_service: UserService | None = None) -> None:
        self.user_service = user_service or UserService()

    def list(self):
        """GET /users"""
        pairs = self.user_service.list_users()
        return jsonify([
            serialize_user(user, task_count=count) for user, count in pairs
        ]), 200

    def get(self, user_id: int):
        """GET /users/<user_id> — só o próprio usuário ou admin/manager."""
        require_self_or_role(user_id, *PRIVILEGED_ROLES)
        user = self.user_service.get_user(user_id)
        tasks = self.user_service.get_user_tasks(user_id)
        return jsonify(serialize_user(user, tasks=serialize_tasks(tasks))), 200

    def create(self):
        """POST /users — registro público."""
        data = user_create_schema.load(json_body())
        user = self.user_service.create_user(data)
        return jsonify(serialize_user(user)), 201

    def update(self, user_id: int):
        """PUT /users/<user_id> — só o próprio usuário ou admin."""
        require_self_or_role(user_id, UserRole.ADMIN.value)
        data = user_update_schema.load(json_body())
        user = self.user_service.update_user(user_id, data)
        return jsonify(serialize_user(user)), 200

    def delete(self, user_id: int):
        """DELETE /users/<user_id> — restrito a admin pela rota."""
        self.user_service.delete_user(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    def list_tasks(self, user_id: int):
        """GET /users/<user_id>/tasks — só o próprio usuário ou admin/manager."""
        require_self_or_role(user_id, *PRIVILEGED_ROLES)
        tasks = self.user_service.get_user_tasks(user_id)
        return jsonify(serialize_tasks(tasks)), 200
