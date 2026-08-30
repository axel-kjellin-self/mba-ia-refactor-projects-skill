"""Notificações de pedido.

Isolar aqui os antigos ``print("ENVIANDO EMAIL: ...")`` dos controllers deixa o
ponto de integração explícito: trocar por um provedor real (fila, SMTP, gateway
de SMS) não exige tocar em nenhuma rota.
"""

import logging

logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id: int, usuario_id: int) -> None:
    logger.info(
        "Notificação de pedido criado enfileirada",
        extra={"pedido_id": pedido_id, "usuario_id": usuario_id},
    )


def notificar_mudanca_de_status(pedido_id: int, novo_status: str) -> None:
    logger.info(
        "Notificação de mudança de status enfileirada",
        extra={"pedido_id": pedido_id, "status": novo_status},
    )
