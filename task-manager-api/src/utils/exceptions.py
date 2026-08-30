"""Exceções de domínio.

Permitem que os services sinalizem falhas de negócio sem conhecer HTTP.
O mapeamento para status code acontece em `middlewares/error_handler.py`.
"""


class DomainError(Exception):
    """Erro de negócio. Mapeado para HTTP 400 por padrão."""

    status_code = 400

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(DomainError):
    """Input inválido — HTTP 400."""

    status_code = 400


class NotFoundError(DomainError):
    """Recurso inexistente — HTTP 404."""

    status_code = 404


class ConflictError(DomainError):
    """Violação de unicidade / estado conflitante — HTTP 409."""

    status_code = 409


class AuthenticationError(DomainError):
    """Credenciais ausentes ou inválidas — HTTP 401."""

    status_code = 401


class AuthorizationError(DomainError):
    """Autenticado, mas sem permissão — HTTP 403."""

    status_code = 403
