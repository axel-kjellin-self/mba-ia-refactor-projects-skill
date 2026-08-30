"""Regras de negócio de produto."""

from src.config.constants import ITENS_POR_PAGINA_PADRAO, PAGINA_PADRAO
from src.repositories import produto_repository
from src.utils.errors import NotFoundError


def _offset(pagina: int, por_pagina: int) -> int:
    return (pagina - 1) * por_pagina


def listar(pagina: int = PAGINA_PADRAO, por_pagina: int = ITENS_POR_PAGINA_PADRAO) -> dict:
    produtos = produto_repository.listar(por_pagina, _offset(pagina, por_pagina))
    return {
        "itens": [produto.to_dict() for produto in produtos],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": produto_repository.contar(),
    }


def buscar(produto_id: int) -> dict:
    produto = produto_repository.buscar_por_id(produto_id)
    if produto is None:
        raise NotFoundError("Produto não encontrado")
    return produto.to_dict()


def pesquisar(
    termo: str | None,
    categoria: str | None,
    preco_min: float | None,
    preco_max: float | None,
    pagina: int = PAGINA_PADRAO,
    por_pagina: int = ITENS_POR_PAGINA_PADRAO,
) -> dict:
    produtos = produto_repository.pesquisar(
        termo, categoria, preco_min, preco_max, por_pagina, _offset(pagina, por_pagina)
    )
    return {
        "itens": [produto.to_dict() for produto in produtos],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": len(produtos),
    }


def criar(dados_validados: dict) -> dict:
    produto_id = produto_repository.inserir(**dados_validados)
    return {"id": produto_id}


def atualizar(produto_id: int, dados_validados: dict) -> None:
    if produto_repository.buscar_por_id(produto_id) is None:
        raise NotFoundError("Produto não encontrado")
    produto_repository.atualizar(produto_id, **dados_validados)


def deletar(produto_id: int) -> None:
    if not produto_repository.deletar(produto_id):
        raise NotFoundError("Produto não encontrado")
