"""Schemas de User — validação de input e serialização de output.

O campo de senha é `load_only` e ausente do schema de resposta: nunca aparece
em resposta alguma da API (corrige o CRITICAL de vazamento do hash em
`to_dict()`).
"""
import re

from marshmallow import Schema, ValidationError, fields, validate, validates

from src.config.constants import (
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    UserRole,
)

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$')


def validate_password_strength(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres'
        )
    checks = (
        (r'[a-z]', 'uma letra minúscula'),
        (r'[A-Z]', 'uma letra maiúscula'),
        (r'\d', 'um número'),
    )
    missing = [label for pattern, label in checks if not re.search(pattern, password)]
    if missing:
        raise ValidationError(f"Senha deve conter ao menos {', '.join(missing)}")


class UserResponseSchema(Schema):
    """Representação pública de um usuário. Sem senha, por construção.

    Campos derivados (`task_count`, `tasks`) não são declarados aqui de
    propósito: são injetados por `serialize_user`, senão o marshmallow
    tentaria serializar o backref `User.tasks` do ORM.
    """

    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    role = fields.Str()
    active = fields.Bool()
    created_at = fields.DateTime()


class UserCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=MAX_NAME_LENGTH))
    email = fields.Str(required=True, validate=validate.Length(max=MAX_EMAIL_LENGTH))
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(
        load_default=UserRole.USER.value, validate=validate.OneOf(UserRole.values())
    )

    @validates('email')
    def _validate_email(self, value: str, **kwargs) -> None:
        if not EMAIL_PATTERN.match(value):
            raise ValidationError('Email inválido')

    @validates('password')
    def _validate_password(self, value: str, **kwargs) -> None:
        validate_password_strength(value)


class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=MAX_NAME_LENGTH))
    email = fields.Str(validate=validate.Length(max=MAX_EMAIL_LENGTH))
    password = fields.Str(load_only=True)
    role = fields.Str(validate=validate.OneOf(UserRole.values()))
    active = fields.Bool()

    @validates('email')
    def _validate_email(self, value: str, **kwargs) -> None:
        if not EMAIL_PATTERN.match(value):
            raise ValidationError('Email inválido')

    @validates('password')
    def _validate_password(self, value: str, **kwargs) -> None:
        validate_password_strength(value)


class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


user_response_schema = UserResponseSchema()
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()


def serialize_user(user, **extra) -> dict:
    data = user_response_schema.dump(user)
    data.update(extra)
    return data


def serialize_users(users) -> list[dict]:
    return [serialize_user(user) for user in users]
