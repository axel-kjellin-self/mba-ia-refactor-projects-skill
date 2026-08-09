from marshmallow import Schema, fields, validate
from src.config.constants import ValidationRules


class CategorySchema(Schema):
    """Schema for category serialization"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(
        max=ValidationRules.MAX_CATEGORY_NAME_LENGTH
    ))
    description = fields.Str(allow_none=True, validate=validate.Length(
        max=ValidationRules.MAX_CATEGORY_DESC_LENGTH
    ))
    color = fields.Str(missing='#000000')
    created_at = fields.DateTime(dump_only=True)
    task_count = fields.Int(dump_only=True)


class CategoryCreateSchema(Schema):
    """Schema for category creation"""
    name = fields.Str(required=True, validate=validate.Length(
        max=ValidationRules.MAX_CATEGORY_NAME_LENGTH
    ))
    description = fields.Str(allow_none=True)
    color = fields.Str(missing='#000000')


class CategoryUpdateSchema(Schema):
    """Schema for category update"""
    name = fields.Str(validate=validate.Length(
        max=ValidationRules.MAX_CATEGORY_NAME_LENGTH
    ))
    description = fields.Str(allow_none=True)
    color = fields.Str()


# Schema instances
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()
