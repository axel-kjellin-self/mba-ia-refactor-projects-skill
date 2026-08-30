"""Helpers HTTP compartilhados pelos controllers."""

from flask import jsonify, request

from src.config.constants import (
    ITENS_POR_PAGINA_MAXIMO,
    ITENS_POR_PAGINA_PADRAO,
    PAGINA_PADRAO,
)
from src.schemas import validators


def sucesso(dados=None, status: int = 200, mensagem: str | None = None):
    corpo = {"sucesso": True}
    if dados is not None:
        corpo["dados"] = dados
    if mensagem:
        corpo["mensagem"] = mensagem
    return jsonify(corpo), status


def parametros_de_paginacao() -> tuple:
    pagina = validators.inteiro_de_query(
        request.args.get("pagina"), "pagina", PAGINA_PADRAO, 1, 1_000_000
    )
    por_pagina = validators.inteiro_de_query(
        request.args.get("por_pagina"),
        "por_pagina",
        ITENS_POR_PAGINA_PADRAO,
        1,
        ITENS_POR_PAGINA_MAXIMO,
    )
    return pagina, por_pagina
