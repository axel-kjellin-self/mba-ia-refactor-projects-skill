from flask import request, jsonify
from src.services.task_service import TaskService
from src.schemas.task_schema import task_schema, tasks_schema, task_create_schema, task_update_schema
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)


class TaskController:
    """HTTP controller for task endpoints"""

    def __init__(self):
        self.task_service = TaskService()

    def get_all(self):
        """GET /tasks"""
        try:
            tasks = self.task_service.get_all_tasks()
            return jsonify(tasks), 200

        except Exception as e:
            logger.error(f"Error getting tasks: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    def get_by_id(self, task_id):
        """GET /tasks/<id>"""
        try:
            task = self.task_service.get_task_by_id(task_id)
            return jsonify(task.to_dict()), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def create(self):
        """POST /tasks"""
        try:
            # Validate input
            data = task_create_schema.load(request.get_json())

            # Create task
            task = self.task_service.create_task(data)

            return jsonify(task_schema.dump(task)), 201

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    def update(self, task_id):
        """PUT /tasks/<id>"""
        try:
            # Validate input
            data = task_update_schema.load(request.get_json())

            # Update task
            task = self.task_service.update_task(task_id, data)

            return jsonify(task_schema.dump(task)), 200

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def delete(self, task_id):
        """DELETE /tasks/<id>"""
        try:
            self.task_service.delete_task(task_id)
            return jsonify({'message': 'Task deleted successfully'}), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def search(self):
        """GET /tasks/search"""
        query = request.args.get('q')
        status = request.args.get('status')
        priority = request.args.get('priority')
        user_id = request.args.get('user_id')

        tasks = self.task_service.search_tasks(query, status, priority, user_id)

        return jsonify(tasks_schema.dump(tasks)), 200

    def get_stats(self):
        """GET /tasks/stats"""
        stats = self.task_service.get_task_stats()
        return jsonify(stats), 200
