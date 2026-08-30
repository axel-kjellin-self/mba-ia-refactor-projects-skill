"""Controllers de pedido."""

from flask import request

from src.controllers.http import parametros_de_paginacao, sucesso
from src.middlewares.auth import carregar_usuario_autenticado
from src.schemas.pedido_schema import validar_novo_pedido, validar_status
from src.services import pedido_service


def criar_pedido():
    # O dono do pedido vem do token, não do corpo: no legado qualquer um podia
    # criar pedidos em nome de outro usuário informando "usuario_id".
    usuario = carregar_usuario_autenticado()
    dados = validar_novo_pedido(request.get_json(silent=True))
    resultado = pedido_service.criar(usuario.id, dados)
    return sucesso(resultado, status=201, mensagem="Pedido criado com sucesso")


def listar_todos_pedidos():
    pagina, por_pagina = parametros_de_paginacao()
    return sucesso(pedido_service.listar_todos(pagina, por_pagina))


def listar_pedidos_usuario(usuario_id: int):
    solicitante = carregar_usuario_autenticado()
    pagina, por_pagina = parametros_de_paginacao()
    return sucesso(
        pedido_service.listar_do_usuario(usuario_id, solicitante, pagina, por_pagina)
    )


def atualizar_status_pedido(pedido_id: int):
    novo_status = validar_status(request.get_json(silent=True))
    resultado = pedido_service.atualizar_status(pedido_id, novo_status)
    return sucesso(resultado, mensagem="Status atualizado")
