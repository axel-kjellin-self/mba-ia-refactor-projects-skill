"""Notificações de pedido.

Isola os ``print("ENVIANDO EMAIL: ...")`` que estavam embutidos no controller.
A implementação continua sendo apenas log — o ponto é que o restante do código
passa a depender de uma interface, e trocar por um provedor real (fila, SMTP,
gateway de SMS) não exige tocar em controllers ou services de pedido.
"""

import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de notificações. Implementação atual: registro em log."""

    def pedido_criado(self, pedido_id: int, usuario_id: int, total: float) -> None:
        logger.info(
            "Notificação de pedido criado", extra={"pedido_id": pedido_id, "usuario_id": usuario_id}
        )
        self._enviar("email", f"Pedido {pedido_id} criado. Total: R$ {total:.2f}")
        self._enviar("sms", f"Seu pedido {pedido_id} foi recebido!")

    def status_alterado(self, pedido_id: int, status: str) -> None:
        logger.info(
            "Notificação de mudança de status",
            extra={"pedido_id": pedido_id, "status": status},
        )
        self._enviar("email", f"Pedido {pedido_id} agora está '{status}'.")

    def _enviar(self, canal: str, mensagem: str) -> None:
        # Ponto de extensão: substituir por integração real mantendo a assinatura.
        logger.debug("[%s] %s", canal, mensagem)
