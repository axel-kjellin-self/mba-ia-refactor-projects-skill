"""Controller de autenticação. Só HTTP: valida input, delega, formata output."""
from flask import jsonify

from src.controllers.http import json_body
from src.schemas.user_schema import login_schema, serialize_user
from src.services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService | None = None) -> None:
        self.auth_service = auth_service or AuthService()

    def login(self):
        """POST /login — devolve um JWT assinado."""
        credentials = login_schema.load(json_body())
        user, token = self.auth_service.authenticate(
            credentials['email'], credentials['password']
        )
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': serialize_user(user),
            'token': token,
            'token_type': 'Bearer',
        }), 200
