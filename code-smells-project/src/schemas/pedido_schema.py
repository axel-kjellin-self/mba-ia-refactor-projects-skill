"""Schemas de entrada para pedidos."""

from typing import Any

from src.config.constants import RegrasValidacao, StatusPedido
from src.models.pedido import ItemPedidoInput
from src.schemas import validators
from src.utils.errors import ValidationError


def carregar_itens(dados: Any) -> list[ItemPedidoInput]:
    """Valida a lista de itens de um pedido.

    ``quantidade`` exige inteiro estritamente positivo: no código original um
    valor negativo passava direto, aumentando o estoque e produzindo um pedido
    de total negativo.
    """
    dados = validators.exigir_objeto(dados)
    itens_brutos = validators.lista(
        dados, "itens", minimo=1, maximo=RegrasValidacao.ITENS_PEDIDO_MAX
    )

    itens: list[ItemPedidoInput] = []
    vistos: set[int] = set()

    for indice, bruto in enumerate(itens_brutos):
        if not isinstance(bruto, dict):
            raise ValidationError(f"Item {indice} deve ser um objeto.")

        produto_id = validators.inteiro(bruto, "produto_id", minimo=1)
        quantidade = validators.inteiro(
            bruto, "quantidade", minimo=1, maximo=RegrasValidacao.QUANTIDADE_MAX
        )

        if produto_id in vistos:
            raise ValidationError(
                f"Produto {produto_id} aparece mais de uma vez; "
                "agregue as quantidades em um único item."
            )
        vistos.add(produto_id)

        itens.append(ItemPedidoInput(produto_id=produto_id, quantidade=quantidade))

    return itens


def carregar_status(dados: Any) -> str:
    """Valida a transição de status de um pedido."""
    dados = validators.exigir_objeto(dados)
    return validators.escolha(dados, "status", StatusPedido.VALIDOS)
