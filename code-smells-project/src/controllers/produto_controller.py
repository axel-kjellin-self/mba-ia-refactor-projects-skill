"""Controllers de produto: apenas tradução HTTP ↔ service.

Sem try/except: erros de domínio sobem para o error handler global, que decide
o status code.
"""

from flask import request

from src.controllers.http import parametros_de_paginacao, sucesso
from src.schemas import validators
from src.schemas.produto_schema import validar_produto
from src.services import produto_service


def listar_produtos():
    pagina, por_pagina = parametros_de_paginacao()
    return sucesso(produto_service.listar(pagina, por_pagina))


def buscar_produtos():
    pagina, por_pagina = parametros_de_paginacao()
    resultado = produto_service.pesquisar(
        termo=request.args.get("q", "").strip() or None,
        categoria=request.args.get("categoria", "").strip().lower() or None,
        preco_min=validators.numero_de_query(request.args.get("preco_min"), "preco_min", 0),
        preco_max=validators.numero_de_query(request.args.get("preco_max"), "preco_max", 0),
        pagina=pagina,
        por_pagina=por_pagina,
    )
    return sucesso(resultado)


def buscar_produto(produto_id: int):
    return sucesso(produto_service.buscar(produto_id))


def criar_produto():
    dados = validar_produto(request.get_json(silent=True))
    return sucesso(produto_service.criar(dados), status=201, mensagem="Produto criado")


def atualizar_produto(produto_id: int):
    dados = validar_produto(request.get_json(silent=True))
    produto_service.atualizar(produto_id, dados)
    return sucesso(mensagem="Produto atualizado")


def deletar_produto(produto_id: int):
    produto_service.deletar(produto_id)
    return sucesso(mensagem="Produto deletado")
