"""Schemas de entrada para produtos."""

from dataclasses import dataclass
from typing import Any

from src.config.constants import Categoria, Paginacao, RegrasValidacao
from src.schemas import validators


@dataclass(frozen=True, slots=True)
class ProdutoInput:
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str


@dataclass(frozen=True, slots=True)
class BuscaProdutoInput:
    termo: str | None
    categoria: str | None
    preco_min: float | None
    preco_max: float | None
    limite: int
    offset: int


def carregar_produto(dados: Any) -> ProdutoInput:
    """Valida o payload de criação/atualização de produto.

    A mesma validação atende POST e PUT — antes, o PUT deixava de validar
    categoria, aceitando valores que o POST rejeitava.
    """
    dados = validators.exigir_objeto(dados)

    return ProdutoInput(
        nome=validators.texto(
            dados,
            "nome",
            minimo=RegrasValidacao.NOME_PRODUTO_MIN,
            maximo=RegrasValidacao.NOME_PRODUTO_MAX,
        ),
        descricao=validators.texto(
            dados,
            "descricao",
            obrigatorio=False,
            maximo=RegrasValidacao.DESCRICAO_MAX,
            padrao="",
        ),
        preco=validators.numero(
            dados, "preco", minimo=0, maximo=RegrasValidacao.PRECO_MAX
        ),
        estoque=validators.inteiro(
            dados, "estoque", minimo=0, maximo=RegrasValidacao.ESTOQUE_MAX
        ),
        categoria=validators.escolha(
            dados,
            "categoria",
            Categoria.VALIDAS,
            obrigatorio=False,
            padrao=Categoria.PADRAO,
        ),
    )


def carregar_busca(args: dict[str, str]) -> BuscaProdutoInput:
    """Valida os filtros da busca de produtos vindos da query string."""
    categoria = args.get("categoria") or None
    if categoria is not None:
        categoria = validators.escolha({"categoria": categoria}, "categoria", Categoria.VALIDAS)

    preco_min = validators.numero_query(args.get("preco_min"), "preco_min", minimo=0)
    preco_max = validators.numero_query(args.get("preco_max"), "preco_max", minimo=0)

    return BuscaProdutoInput(
        termo=(args.get("q") or "").strip() or None,
        categoria=categoria,
        preco_min=preco_min,
        preco_max=preco_max,
        limite=validators.inteiro_query(
            args.get("limite"),
            "limite",
            padrao=Paginacao.LIMITE_PADRAO,
            minimo=1,
            maximo=Paginacao.LIMITE_MAX,
        ),
        offset=validators.inteiro_query(
            args.get("offset"), "offset", padrao=0, minimo=0, maximo=10**6
        ),
    )
