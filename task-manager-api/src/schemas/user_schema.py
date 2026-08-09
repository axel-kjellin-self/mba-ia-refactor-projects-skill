from marshmallow import Schema, fields, validate, ValidationError
from src.config.constants import ValidationRules


class UserSchema(Schema):
    """Schema for user serialization"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(
        min=ValidationRules.MIN_NAME_LENGTH,
        max=ValidationRules.MAX_NAME_LENGTH
    ))
    email = fields.Email(required=True, validate=validate.Length(
        max=ValidationRules.MAX_EMAIL_LENGTH
    ))
    role = fields.Str(
        validate=validate.OneOf(ValidationRules.VALID_USER_ROLES),
        missing='user'
    )
    active = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)
    task_count = fields.Int(dump_only=True)


class UserCreateSchema(Schema):
    """Schema for user creation"""
    name = fields.Str(required=True, validate=validate.Length(
        min=ValidationRules.MIN_NAME_LENGTH,
        max=ValidationRules.MAX_NAME_LENGTH
    ))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(
        min=ValidationRules.MIN_PASSWORD_LENGTH
    ), load_only=True)
    role = fields.Str(
        validate=validate.OneOf(ValidationRules.VALID_USER_ROLES),
        missing='user'
    )


class UserUpdateSchema(Schema):
    """Schema for user update"""
    name = fields.Str(validate=validate.Length(
        min=ValidationRules.MIN_NAME_LENGTH,
        max=ValidationRules.MAX_NAME_LENGTH
    ))
    email = fields.Email()
    password = fields.Str(validate=validate.Length(
        min=ValidationRules.MIN_PASSWORD_LENGTH
    ), load_only=True)
    role = fields.Str(validate=validate.OneOf(ValidationRules.VALID_USER_ROLES))
    active = fields.Bool()


class LoginSchema(Schema):
    """Schema for login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


# Schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()
