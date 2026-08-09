from marshmallow import Schema, fields, validate
from src.config.constants import ValidationRules


class TaskSchema(Schema):
    """Schema for task serialization"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(
        min=ValidationRules.MIN_TITLE_LENGTH,
        max=ValidationRules.MAX_TITLE_LENGTH
    ))
    description = fields.Str(allow_none=True)
    status = fields.Str(
        validate=validate.OneOf(ValidationRules.VALID_TASK_STATUSES),
        missing='pending'
    )
    priority = fields.Int(
        validate=validate.Range(
            min=ValidationRules.MIN_PRIORITY,
            max=ValidationRules.MAX_PRIORITY
        ),
        missing=3
    )
    user_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    overdue = fields.Bool(dump_only=True)


class TaskCreateSchema(Schema):
    """Schema for task creation"""
    title = fields.Str(required=True, validate=validate.Length(
        min=ValidationRules.MIN_TITLE_LENGTH,
        max=ValidationRules.MAX_TITLE_LENGTH
    ))
    description = fields.Str(allow_none=True)
    status = fields.Str(
        validate=validate.OneOf(ValidationRules.VALID_TASK_STATUSES),
        missing='pending'
    )
    priority = fields.Int(
        validate=validate.Range(
            min=ValidationRules.MIN_PRIORITY,
            max=ValidationRules.MAX_PRIORITY
        ),
        missing=3
    )
    user_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)


class TaskUpdateSchema(Schema):
    """Schema for task update"""
    title = fields.Str(validate=validate.Length(
        min=ValidationRules.MIN_TITLE_LENGTH,
        max=ValidationRules.MAX_TITLE_LENGTH
    ))
    description = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(ValidationRules.VALID_TASK_STATUSES))
    priority = fields.Int(validate=validate.Range(
        min=ValidationRules.MIN_PRIORITY,
        max=ValidationRules.MAX_PRIORITY
    ))
    user_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)


# Schema instances
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()
