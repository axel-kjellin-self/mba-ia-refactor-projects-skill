from flask import request, jsonify
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.schemas.user_schema import (
    user_schema, users_schema,
    user_create_schema, user_update_schema,
    login_schema
)
from src.schemas.task_schema import tasks_schema
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)


class UserController:
    """HTTP controller for user endpoints"""

    def __init__(self):
        self.user_service = UserService()
        self.auth_service = AuthService()

    def get_all(self):
        """GET /users"""
        users = self.user_service.get_all_users()
        return jsonify(users_schema.dump(users)), 200

    def get_by_id(self, user_id):
        """GET /users/<id>"""
        try:
            user = self.user_service.get_user_by_id(user_id)
            data = user.to_dict(include_tasks=True)
            return jsonify(data), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def create(self):
        """POST /users"""
        try:
            data = user_create_schema.load(request.get_json())
            user = self.user_service.create_user(data)

            # Return without password
            return jsonify(user_schema.dump(user)), 201

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 409

    def update(self, user_id):
        """PUT /users/<id>"""
        try:
            data = user_update_schema.load(request.get_json())
            user = self.user_service.update_user(user_id, data)

            return jsonify(user_schema.dump(user)), 200

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def delete(self, user_id):
        """DELETE /users/<id>"""
        try:
            self.user_service.delete_user(user_id)
            return jsonify({'message': 'User deleted successfully'}), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def get_user_tasks(self, user_id):
        """GET /users/<id>/tasks"""
        try:
            tasks = self.user_service.get_user_tasks(user_id)
            result = []
            for task in tasks:
                task_data = task.to_dict()
                result.append(task_data)

            return jsonify(result), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def login(self):
        """POST /login"""
        try:
            data = login_schema.load(request.get_json())

            result = self.auth_service.login(data['email'], data['password'])

            return jsonify(result), 200

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 401
