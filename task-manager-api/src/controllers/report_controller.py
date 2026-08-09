from flask import request, jsonify
from src.services.report_service import ReportService, CategoryService
from src.schemas.category_schema import (
    category_schema, categories_schema,
    category_create_schema, category_update_schema
)
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)


class ReportController:
    """HTTP controller for report endpoints"""

    def __init__(self):
        self.report_service = ReportService()

    def get_summary(self):
        """GET /reports/summary"""
        report = self.report_service.get_summary_report()
        return jsonify(report), 200

    def get_user_report(self, user_id):
        """GET /reports/user/<id>"""
        try:
            report = self.report_service.get_user_report(user_id)
            return jsonify(report), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404


class CategoryController:
    """HTTP controller for category endpoints"""

    def __init__(self):
        self.category_service = CategoryService()

    def get_all(self):
        """GET /categories"""
        categories = self.category_service.get_all_categories()
        return jsonify(categories), 200

    def create(self):
        """POST /categories"""
        try:
            data = category_create_schema.load(request.get_json())
            category = self.category_service.create_category(data)

            return jsonify(category_schema.dump(category)), 201

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

    def update(self, cat_id):
        """PUT /categories/<id>"""
        try:
            data = category_update_schema.load(request.get_json())
            category = self.category_service.update_category(cat_id, data)

            return jsonify(category_schema.dump(category)), 200

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    def delete(self, cat_id):
        """DELETE /categories/<id>"""
        try:
            self.category_service.delete_category(cat_id)
            return jsonify({'message': 'Category deleted'}), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404
