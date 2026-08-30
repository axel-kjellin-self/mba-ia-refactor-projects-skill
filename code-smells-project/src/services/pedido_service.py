"""Regras de negócio de pedidos."""

import logging

from src.config.constants import StatusPedido
from src.config.database import transacao
from src.models.pedido import ItemPedidoInput, Pedido
from src.repositories.pedido_repository import PedidoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.services.notification_service import NotificationService
from src.utils.errors import BusinessRuleError, ConflictError, NotFoundError

logger = logging.getLogger(__name__)

# Estados terminais: um pedido entregue ou cancelado não muda mais de status.
_STATUS_FINAIS = frozenset({StatusPedido.ENTREGUE, StatusPedido.CANCELADO})


class PedidoService:
    def __init__(
        self,
        pedido_repo: PedidoRepository | None = None,
        produto_repo: ProdutoRepository | None = None,
        usuario_repo: UsuarioRepository | None = None,
        notificacoes: NotificationService | None = None,
    ) -> None:
        self.pedido_repo = pedido_repo or PedidoRepository()
        self.produto_repo = produto_repo or ProdutoRepository()
        self.usuario_repo = usuario_repo or UsuarioRepository()
        self.notificacoes = notificacoes or NotificationService()

    def listar(self, limite: int, offset: int = 0) -> list[Pedido]:
        return self.pedido_repo.listar(limite, offset)

    def listar_por_usuario(self, usuario_id: int, limite: int, offset: int = 0) -> list[Pedido]:
        return self.pedido_repo.listar_por_usuario(usuario_id, limite, offset)

    def buscar(self, pedido_id: int) -> Pedido:
        pedido = self.pedido_repo.buscar_por_id(pedido_id)
        if pedido is None:
            raise NotFoundError(f"Pedido {pedido_id} não encontrado.")
        return pedido

    def criar(self, usuario_id: int, itens: list[ItemPedidoInput]) -> Pedido:
        """Cria um pedido validando estoque e baixando o saldo atomicamente.

        Toda a operação — inserção do pedido, dos itens e a baixa de estoque —
        ocorre em uma única transação. Qualquer falha desfaz o conjunto, em vez
        de deixar itens órfãos e estoque decrementado como no fluxo original.
        """
        if self.usuario_repo.buscar_por_id(usuario_id) is None:
            raise NotFoundError(f"Usuário {usuario_id} não encontrado.")

        # Uma única query carrega todos os produtos do pedido.
        produtos = self.produto_repo.buscar_varios_por_id(
            [item.produto_id for item in itens]
        )

        for item in itens:
            produto = produtos.get(item.produto_id)
            if produto is None:
                raise NotFoundError(f"Produto {item.produto_id} não encontrado.")
            if not produto.ativo:
                raise BusinessRuleError(f"Produto '{produto.nome}' está inativo.")
            if produto.estoque < item.quantidade:
                raise BusinessRuleError(
                    f"Estoque insuficiente para '{produto.nome}': "
                    f"disponível {produto.estoque}, solicitado {item.quantidade}."
                )

        total = round(
            sum(produtos[item.produto_id].preco * item.quantidade for item in itens), 2
        )

        with transacao():
            pedido_id = self.pedido_repo.criar(usuario_id, StatusPedido.PENDENTE, total)

            for item in itens:
                produto = produtos[item.produto_id]
                self.pedido_repo.adicionar_item(
                    pedido_id, item.produto_id, item.quantidade, produto.preco
                )

                # A baixa é condicional: se o estoque mudou desde a validação,
                # nenhuma linha é afetada e a transação inteira é revertida.
                if not self.produto_repo.baixar_estoque(item.produto_id, item.quantidade):
                    raise ConflictError(
                        f"Estoque de '{produto.nome}' foi alterado durante o pedido. "
                        "Tente novamente."
                    )

        pedido = self.buscar(pedido_id)
        self.notificacoes.pedido_criado(pedido_id, usuario_id, total)
        return pedido

    def atualizar_status(self, pedido_id: int, novo_status: str) -> Pedido:
        """Altera o status do pedido, repondo o estoque em cancelamentos."""
        pedido = self.buscar(pedido_id)

        if pedido.status == novo_status:
            return pedido

        if pedido.status in _STATUS_FINAIS:
            raise BusinessRuleError(
                f"Pedido {pedido_id} está '{pedido.status}' e não pode mudar de status."
            )

        with transacao():
            self.pedido_repo.atualizar_status(pedido_id, novo_status)

            # O código original apenas imprimia "Devolver estoque" e nunca devolvia.
            if novo_status == StatusPedido.CANCELADO:
                for item in pedido.itens:
                    self.produto_repo.repor_estoque(item.produto_id, item.quantidade)
                logger.info("Estoque reposto para o pedido %s", pedido_id)

        self.notificacoes.status_alterado(pedido_id, novo_status)
        return self.buscar(pedido_id)
