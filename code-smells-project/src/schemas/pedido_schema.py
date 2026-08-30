"""Validação de payloads de pedido."""

from src.config.constants import (
    ITENS_MAXIMOS_POR_PEDIDO,
    QUANTIDADE_MAXIMA_POR_ITEM,
    STATUS_PEDIDO_VALIDOS,
)
from src.schemas import validators
from src.utils.errors import ValidationError


def validar_novo_pedido(dados) -> dict:
    dados = validators.exigir_dict(dados)
    itens_brutos = dados.get("itens")

    if not isinstance(itens_brutos, list) or not itens_brutos:
        raise ValidationError("'itens' deve ser uma lista com ao menos 1 item")
    if len(itens_brutos) > ITENS_MAXIMOS_POR_PEDIDO:
        raise ValidationError(
            f"Um pedido pode ter no máximo {ITENS_MAXIMOS_POR_PEDIDO} itens"
        )

    itens = []
    for posicao, item in enumerate(itens_brutos):
        if not isinstance(item, dict):
            raise ValidationError(f"Item na posição {posicao} deve ser um objeto")
        itens.append(
            {
                "produto_id": validators.inteiro(item, "produto_id", minimo=1),
                "quantidade": validators.inteiro(
                    item, "quantidade", minimo=1, maximo=QUANTIDADE_MAXIMA_POR_ITEM
                ),
            }
        )

    return {"itens": itens}


def validar_status(dados) -> str:
    dados = validators.exigir_dict(dados)
    status = validators.texto(dados, "status").lower()
    return validators.opcao(status, "status", STATUS_PEDIDO_VALIDOS)
