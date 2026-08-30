"""Schemas de Task — fonte única da serialização.

Antes a mesma Task era serializada de três formas diferentes (em
`Task.to_dict()`, em `GET /tasks` e em `GET /users/<id>/tasks`), com o campo
`overdue` recalculado em quatro lugares.
"""
from marshmallow import Schema, fields, validate

from src.config.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    MAX_DESCRIPTION_LENGTH,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    TaskStatus,
)

_title = validate.Length(min=MIN_TITLE_LENGTH, max=MAX_TITLE_LENGTH)
_priority = validate.Range(min=MIN_PRIORITY, max=MAX_PRIORITY)
_status = validate.OneOf(TaskStatus.values())


class TaskCreateSchema(Schema):
    title = fields.Str(required=True, validate=_title)
    description = fields.Str(
        load_default='', allow_none=True, validate=validate.Length(max=MAX_DESCRIPTION_LENGTH)
    )
    status = fields.Str(load_default=TaskStatus.PENDING.value, validate=_status)
    priority = fields.Int(load_default=DEFAULT_PRIORITY, validate=_priority)
    user_id = fields.Int(load_default=None, allow_none=True)
    category_id = fields.Int(load_default=None, allow_none=True)
    due_date = fields.DateTime(format=DATE_FORMAT, load_default=None, allow_none=True)
    tags = fields.List(fields.Str(), load_default=None, allow_none=True)


class TaskUpdateSchema(Schema):
    """Todos os campos opcionais — apenas os presentes no body são aplicados."""

    title = fields.Str(validate=_title)
    description = fields.Str(
        allow_none=True, validate=validate.Length(max=MAX_DESCRIPTION_LENGTH)
    )
    status = fields.Str(validate=_status)
    priority = fields.Int(validate=_priority)
    user_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(format=DATE_FORMAT, allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)


class TaskSearchSchema(Schema):
    """Query string de `GET /tasks/search` — converte e valida os tipos.

    Antes `int(priority)` sem try/except transformava `?priority=abc` num 500.
    """

    q = fields.Str(load_default=None, allow_none=True)
    status = fields.Str(load_default=None, allow_none=True, validate=_status)
    priority = fields.Int(load_default=None, allow_none=True, validate=_priority)
    user_id = fields.Int(load_default=None, allow_none=True)


task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()
task_search_schema = TaskSearchSchema()


def serialize_task(task, include_relations: bool = False) -> dict:
    """Representação canônica de uma Task."""
    data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'user_id': task.user_id,
        'category_id': task.category_id,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'tags': task.tag_list,
        'overdue': task.is_overdue,
    }
    if include_relations:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def serialize_tasks(tasks, include_relations: bool = False) -> list[dict]:
    return [serialize_task(task, include_relations) for task in tasks]
