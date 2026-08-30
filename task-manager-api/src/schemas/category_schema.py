"""Schemas de Category — validação de input e serialização de output."""
from marshmallow import Schema, fields, validate

from src.config.constants import (
    DEFAULT_COLOR,
    HEX_COLOR_PATTERN,
    MAX_CATEGORY_DESCRIPTION_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
)

_name = validate.Length(min=1, max=MAX_CATEGORY_NAME_LENGTH)
_description = validate.Length(max=MAX_CATEGORY_DESCRIPTION_LENGTH)
_color = validate.Regexp(HEX_COLOR_PATTERN, error='Cor deve estar no formato hexadecimal #RRGGBB')


class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=_name)
    description = fields.Str(load_default='', allow_none=True, validate=_description)
    color = fields.Str(load_default=DEFAULT_COLOR, validate=_color)


class CategoryUpdateSchema(Schema):
    name = fields.Str(validate=_name)
    description = fields.Str(allow_none=True, validate=_description)
    color = fields.Str(validate=_color)


category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()


def serialize_category(category, task_count: int | None = None) -> dict:
    data = {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': category.created_at.isoformat() if category.created_at else None,
    }
    if task_count is not None:
        data['task_count'] = task_count
    return data
