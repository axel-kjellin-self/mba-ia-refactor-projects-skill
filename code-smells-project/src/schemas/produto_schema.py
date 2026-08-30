"""Validação de payloads de produto.

Criação e atualização compartilham o mesmo validador — no legado eram dois
blocos duplicados que já haviam divergido (a atualização não checava categoria).
"""

from src.config.constants import (
    CATEGORIAS_VALIDAS,
    CATEGORIA_PADRAO,
    NOME_PRODUTO_TAMANHO_MAXIMO,
    NOME_PRODUTO_TAMANHO_MINIMO,
)
from src.schemas import validators


def validar_produto(dados) -> dict:
    dados = validators.exigir_dict(dados)
    categoria = validators.texto(
        dados, "categoria", obrigatorio=False, padrao=CATEGORIA_PADRAO
    ).lower() or CATEGORIA_PADRAO

    return {
        "nome": validators.texto(
            dados,
            "nome",
            minimo=NOME_PRODUTO_TAMANHO_MINIMO,
            maximo=NOME_PRODUTO_TAMANHO_MAXIMO,
        ),
        "descricao": validators.texto(
            dados, "descricao", obrigatorio=False, maximo=2000, padrao=""
        ),
        "preco": validators.numero(dados, "preco", minimo=0),
        "estoque": validators.inteiro(dados, "estoque", minimo=0),
        "categoria": validators.opcao(categoria, "categoria", CATEGORIAS_VALIDAS),
    }
