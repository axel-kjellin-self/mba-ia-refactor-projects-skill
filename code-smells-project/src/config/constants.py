"""Constantes de domínio.

Centraliza os valores que antes apareciam como literais espalhados em
``models.py`` (faixas de desconto) e ``controllers.py`` (categorias, status,
limites de tamanho).
"""

from typing import Final


class Categoria:
    """Categorias aceitas para um produto."""

    VALIDAS: Final[tuple[str, ...]] = (
        "informatica",
        "moveis",
        "vestuario",
        "geral",
        "eletronicos",
        "livros",
    )
    PADRAO: Final[str] = "geral"


class StatusPedido:
    """Ciclo de vida de um pedido."""

    PENDENTE: Final[str] = "pendente"
    APROVADO: Final[str] = "aprovado"
    ENVIADO: Final[str] = "enviado"
    ENTREGUE: Final[str] = "entregue"
    CANCELADO: Final[str] = "cancelado"

    VALIDOS: Final[tuple[str, ...]] = (
        PENDENTE,
        APROVADO,
        ENVIADO,
        ENTREGUE,
        CANCELADO,
    )


class TipoUsuario:
    """Papéis de usuário usados na autorização."""

    ADMIN: Final[str] = "admin"
    CLIENTE: Final[str] = "cliente"

    VALIDOS: Final[tuple[str, ...]] = (ADMIN, CLIENTE)


class FaixaDesconto:
    """Faixas progressivas de desconto sobre o faturamento bruto.

    Avaliadas da maior para a menor; a primeira faixa atingida define a taxa.
    """

    FAIXAS: Final[tuple[tuple[float, float], ...]] = (
        (10_000.0, 0.10),
        (5_000.0, 0.05),
        (1_000.0, 0.02),
    )


class RegrasValidacao:
    """Limites de validação de entrada."""

    NOME_PRODUTO_MIN: Final[int] = 2
    NOME_PRODUTO_MAX: Final[int] = 200
    DESCRICAO_MAX: Final[int] = 1_000

    NOME_USUARIO_MIN: Final[int] = 2
    NOME_USUARIO_MAX: Final[int] = 120
    EMAIL_MAX: Final[int] = 254

    # Elevado dos 0 caracteres efetivos do código original.
    SENHA_MIN: Final[int] = 12
    SENHA_MAX: Final[int] = 128

    PRECO_MAX: Final[float] = 1_000_000.0
    ESTOQUE_MAX: Final[int] = 1_000_000
    QUANTIDADE_MAX: Final[int] = 1_000

    ITENS_PEDIDO_MAX: Final[int] = 100


class Paginacao:
    """Limites de paginação das listagens."""

    LIMITE_PADRAO: Final[int] = 50
    LIMITE_MAX: Final[int] = 200
