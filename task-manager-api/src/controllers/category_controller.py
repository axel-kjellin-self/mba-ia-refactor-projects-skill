"""Controller de categorias."""
from flask import jsonify

from src.controllers.http import json_body
from src.schemas.category_schema import (
    category_create_schema,
    category_update_schema,
    serialize_category,
)
from src.services.category_service import CategoryService


class CategoryController:
    def __init__(self, category_service: CategoryService | None = None) -> None:
        self.category_service = category_service or CategoryService()

    def list(self):
        """GET /categories"""
        pairs = self.category_service.list_categories()
        return jsonify([
            serialize_category(category, task_count=count) for category, count in pairs
        ]), 200

    def create(self):
        """POST /categories"""
        data = category_create_schema.load(json_body())
        category = self.category_service.create_category(data)
        return jsonify(serialize_category(category)), 201

    def update(self, category_id: int):
        """PUT /categories/<category_id>"""
        data = category_update_schema.load(json_body())
        category = self.category_service.update_category(category_id, data)
        return jsonify(serialize_category(category)), 200

    def delete(self, category_id: int):
        """DELETE /categories/<category_id>"""
        self.category_service.delete_category(category_id)
        return jsonify({'message': 'Categoria deletada'}), 200
