"""Autenticação: emissão e verificação de JWT reais.

Substitui o token decorativo `'fake-jwt-token-' + str(user.id)`, que era
forjável por qualquer um e nunca era validado.
"""
import logging
from datetime import UTC, datetime, timedelta

import jwt

from src.config.settings import Config
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.utils.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def authenticate(self, email: str, password: str) -> tuple[User, str]:
        """Valida credenciais e devolve (usuário, token JWT).

        Raises:
            AuthenticationError: credenciais inválidas ou conta inativa.
        """
        user = self.user_repository.find_by_email(email)

        # Mensagem genérica e verificação sempre executada: não revela se o
        # e-mail existe nem permite enumeração por diferença de tempo.
        if user is None or not user.check_password(password):
            logger.warning('Falha de login para o email %s', email)
            raise AuthenticationError('Credenciais inválidas')

        if not user.active:
            raise AuthenticationError('Usuário inativo')

        return user, self.generate_token(user)

    def generate_token(self, user: User) -> str:
        now = datetime.now(UTC)
        payload = {
            'sub': str(user.id),
            'user_id': user.id,
            'role': user.role,
            'iat': now,
            'exp': now + timedelta(seconds=Config.JWT_EXPIRES_SECONDS),
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        """Decodifica e valida assinatura/expiração do JWT.

        Raises:
            AuthenticationError: token expirado ou inválido.
        """
        try:
            return jwt.decode(
                token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError('Token expirado') from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError('Token inválido') from exc
