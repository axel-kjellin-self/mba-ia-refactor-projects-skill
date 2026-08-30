"""Controller de tasks. Sem queries, sem regras de negócio, sem cálculos."""
from flask import jsonify, request

from src.controllers.http import json_body
from src.schemas.task_schema import (
    serialize_task,
    serialize_tasks,
    task_create_schema,
    task_search_schema,
    task_update_schema,
)
from src.services.task_service import TaskService


class TaskController:
    def __init__(self, task_service: TaskService | None = None) -> None:
        self.task_service = task_service or TaskService()

    def list(self):
        """GET /tasks"""
        tasks = self.task_service.list_tasks()
        return jsonify(serialize_tasks(tasks, include_relations=True)), 200

    def get(self, task_id: int):
        """GET /tasks/<task_id>"""
        task = self.task_service.get_task(task_id)
        return jsonify(serialize_task(task)), 200

    def create(self):
        """POST /tasks"""
        data = task_create_schema.load(json_body())
        task = self.task_service.create_task(data)
        return jsonify(serialize_task(task)), 201

    def update(self, task_id: int):
        """PUT /tasks/<task_id>"""
        data = task_update_schema.load(json_body())
        task = self.task_service.update_task(task_id, data)
        return jsonify(serialize_task(task)), 200

    def delete(self, task_id: int):
        """DELETE /tasks/<task_id>"""
        self.task_service.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    def search(self):
        """GET /tasks/search?q=&status=&priority=&user_id="""
        filters = task_search_schema.load(request.args.to_dict())
        tasks = self.task_service.search_tasks(filters)
        return jsonify(serialize_tasks(tasks)), 200

    def stats(self):
        """GET /tasks/stats"""
        return jsonify(self.task_service.get_stats()), 200
