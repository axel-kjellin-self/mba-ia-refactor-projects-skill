"""Helpers HTTP compartilhados pelos controllers."""
from flask import request

from src.utils.exceptions import ValidationError


def json_body() -> dict:
    """Body JSON obrigatório.

    Antes vários handlers chamavam `request.get_json()` e indexavam o resultado
    sem checar `None`, gerando 500 quando o body vinha vazio.
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValidationError('Corpo da requisição deve ser um objeto JSON válido')
    return body
