"""Exceções de domínio.

Permitem que services sinalizem falhas sem conhecer HTTP. O mapeamento para
status codes acontece em ``middlewares/error_handler.py``.

Substitui o padrão anterior de retornar ``{"erro": ...}`` como valor de
retorno, que obrigava o chamador a inspecionar o dicionário para saber se a
operação falhou.
"""


class AppError(Exception):
    """Erro de aplicação com status HTTP associado."""

    status_code: int = 400

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    """Entrada malformada ou fora das regras de validação."""

    status_code = 400

    def __init__(self, message: str, fields: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.fields = fields or {}


class UnauthorizedError(AppError):
    """Credenciais ausentes ou inválidas."""

    status_code = 401


class ForbiddenError(AppError):
    """Autenticado, mas sem permissão para o recurso."""

    status_code = 403


class NotFoundError(AppError):
    """Recurso inexistente."""

    status_code = 404


class ConflictError(AppError):
    """Violação de unicidade ou de estado (ex.: email já cadastrado)."""

    status_code = 409


class BusinessRuleError(AppError):
    """Regra de negócio violada (ex.: estoque insuficiente)."""

    status_code = 422
