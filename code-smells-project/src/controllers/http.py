"""Helpers de resposta HTTP.

Padroniza o envelope ``{"dados"/"erro", "sucesso"}`` já usado pela API,
eliminando a montagem manual repetida em cada handler.
"""

from typing import Any

from flask import Response, jsonify, request

from src.config.constants import Paginacao
from src.schemas import validators


def ok(dados: Any, status: int = 200, **extras: Any) -> tuple[Response, int]:
    corpo: dict[str, Any] = {"dados": dados, "sucesso": True}
    corpo.update(extras)
    return jsonify(corpo), status


def mensagem(texto: str, status: int = 200, **extras: Any) -> tuple[Response, int]:
    corpo: dict[str, Any] = {"mensagem": texto, "sucesso": True}
    corpo.update(extras)
    return jsonify(corpo), status


def corpo_json() -> Any:
    """Lê o corpo JSON sem levantar 500 quando o payload é inválido."""
    return request.get_json(silent=True)


def paginacao() -> tuple[int, int]:
    """Extrai e valida ``limite`` e ``offset`` da query string."""
    limite = validators.inteiro_query(
        request.args.get("limite"),
        "limite",
        padrao=Paginacao.LIMITE_PADRAO,
        minimo=1,
        maximo=Paginacao.LIMITE_MAX,
    )
    offset = validators.inteiro_query(
        request.args.get("offset"), "offset", padrao=0, minimo=0, maximo=10**6
    )
    return limite, offset
