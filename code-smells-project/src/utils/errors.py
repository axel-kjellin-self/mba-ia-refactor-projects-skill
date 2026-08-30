"""Exceções de domínio.

Os services levantam estas exceções sem conhecer HTTP; o error handler global
as traduz para o status code correto. Isso substitui os ``except Exception`` que
devolviam 500 (e a mensagem interna) para qualquer falha.
"""


class AppError(Exception):
    """Erro de aplicação previsto, com status HTTP associado."""

    status_code = 500
    mensagem_padrao = "Erro interno"

    def __init__(self, mensagem: str = "", detalhes: dict | None = None):
        super().__init__(mensagem or self.mensagem_padrao)
        self.mensagem = mensagem or self.mensagem_padrao
        self.detalhes = detalhes or {}


class ValidationError(AppError):
    status_code = 400
    mensagem_padrao = "Dados inválidos"


class UnauthorizedError(AppError):
    status_code = 401
    mensagem_padrao = "Autenticação necessária"


class ForbiddenError(AppError):
    status_code = 403
    mensagem_padrao = "Acesso negado"


class NotFoundError(AppError):
    status_code = 404
    mensagem_padrao = "Recurso não encontrado"


class ConflictError(AppError):
    """Estado atual do recurso impede a operação (ex.: email já cadastrado)."""

    status_code = 409
    mensagem_padrao = "Conflito com o estado atual do recurso"


class BusinessRuleError(AppError):
    """Regra de negócio violada (ex.: estoque insuficiente)."""

    status_code = 422
    mensagem_padrao = "Operação não permitida pelas regras de negócio"
