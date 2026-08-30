"""Regras de negócio de pedido.

Criação e cancelamento rodam dentro de uma transação única: no legado, uma falha
no meio do processo deixava pedido sem itens ou estoque debitado sem pedido.
"""

import logging

from src.config.constants import (
    ITENS_POR_PAGINA_PADRAO,
    PAGINA_PADRAO,
    STATUS_CANCELADO,
    STATUS_PENDENTE,
)
from src.config.database import transaction
from src.repositories import pedido_repository, produto_repository, usuario_repository
from src.services import notification_service
from src.utils.errors import BusinessRuleError, ForbiddenError, NotFoundError

logger = logging.getLogger(__name__)


def criar(usuario_id: int, dados_validados: dict) -> dict:
    if not usuario_repository.existe(usuario_id):
        raise NotFoundError("Usuário não encontrado")

    itens = _consolidar_itens(dados_validados["itens"])
    produtos = produto_repository.buscar_varios_por_id(item["produto_id"] for item in itens)

    itens_do_pedido = []
    total = 0.0
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise NotFoundError(f"Produto {item['produto_id']} não encontrado")
        if not produto.ativo:
            raise BusinessRuleError(f"Produto '{produto.nome}' está indisponível")
        if produto.estoque < item["quantidade"]:
            raise BusinessRuleError(f"Estoque insuficiente para '{produto.nome}'")

        total += produto.preco * item["quantidade"]
        itens_do_pedido.append({**item, "preco_unitario": produto.preco})

    with transaction() as conexao:
        pedido_id = pedido_repository.inserir(
            conexao, usuario_id, STATUS_PENDENTE, round(total, 2)
        )
        pedido_repository.inserir_itens(conexao, pedido_id, itens_do_pedido)
        for item in itens_do_pedido:
            # Débito condicional: se o estoque mudou entre a checagem acima e
            # este UPDATE, a transação inteira é revertida.
            if not produto_repository.debitar_estoque(
                conexao, item["produto_id"], item["quantidade"]
            ):
                raise BusinessRuleError(
                    f"Estoque insuficiente para o produto {item['produto_id']}"
                )

    notification_service.notificar_pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": round(total, 2)}


def _consolidar_itens(itens: list) -> list:
    """Soma as quantidades do mesmo produto repetido no payload."""
    consolidados: dict = {}
    for item in itens:
        produto_id = item["produto_id"]
        consolidados[produto_id] = consolidados.get(produto_id, 0) + item["quantidade"]
    return [
        {"produto_id": produto_id, "quantidade": quantidade}
        for produto_id, quantidade in consolidados.items()
    ]


def listar_todos(pagina: int = PAGINA_PADRAO, por_pagina: int = ITENS_POR_PAGINA_PADRAO) -> dict:
    pedidos = pedido_repository.listar(por_pagina, (pagina - 1) * por_pagina)
    return {
        "itens": [pedido.to_dict() for pedido in pedidos],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": pedido_repository.contar(),
    }


def listar_do_usuario(
    usuario_id: int,
    solicitante,
    pagina: int = PAGINA_PADRAO,
    por_pagina: int = ITENS_POR_PAGINA_PADRAO,
) -> dict:
    """Aplica a checagem de ownership ausente no legado (IDOR)."""
    if not solicitante.is_admin and solicitante.id != usuario_id:
        raise ForbiddenError("Você só pode consultar os seus próprios pedidos")

    pedidos = pedido_repository.listar_por_usuario(
        usuario_id, por_pagina, (pagina - 1) * por_pagina
    )
    return {
        "itens": [pedido.to_dict() for pedido in pedidos],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": pedido_repository.contar_por_usuario(usuario_id),
    }


def atualizar_status(pedido_id: int, novo_status: str) -> dict:
    pedido = pedido_repository.buscar_por_id(pedido_id)
    if pedido is None:
        raise NotFoundError("Pedido não encontrado")
    if pedido.status == novo_status:
        return {"status": novo_status}
    if pedido.status == STATUS_CANCELADO:
        raise BusinessRuleError("Um pedido cancelado não pode mudar de status")

    with transaction() as conexao:
        pedido_repository.atualizar_status(conexao, pedido_id, novo_status)
        if novo_status == STATUS_CANCELADO:
            # O legado apenas logava "devolver estoque" e nunca devolvia.
            for item in pedido_repository.listar_itens_brutos(pedido_id):
                produto_repository.creditar_estoque(
                    conexao, item["produto_id"], item["quantidade"]
                )

    notification_service.notificar_mudanca_de_status(pedido_id, novo_status)
    return {"status": novo_status}
