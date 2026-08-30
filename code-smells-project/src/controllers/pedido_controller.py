"""Controller HTTP de pedidos."""

from src.controllers import http
from src.middlewares.auth import usuario_atual
from src.schemas.pedido_schema import carregar_itens, carregar_status
from src.services.pedido_service import PedidoService
from src.utils.errors import NotFoundError


class PedidoController:
    def __init__(self, servico: PedidoService | None = None) -> None:
        self.servico = servico or PedidoService()

    def criar(self):
        """POST /pedidos

        O dono do pedido vem do token, não do corpo do request: aceitar
        ``usuario_id`` do cliente permitiria criar pedidos em nome de terceiros.
        """
        itens = carregar_itens(http.corpo_json())
        pedido = self.servico.criar(usuario_atual().id, itens)
        return http.ok(pedido.to_dict(), status=201, mensagem="Pedido criado com sucesso.")

    def listar_todos(self):
        """GET /pedidos — restrito a administradores."""
        limite, offset = http.paginacao()
        pedidos = self.servico.listar(limite, offset)
        return http.ok([p.to_dict() for p in pedidos], total=len(pedidos))

    def listar_por_usuario(self, usuario_id: int):
        """GET /pedidos/usuario/<usuario_id> — próprio usuário ou administrador."""
        limite, offset = http.paginacao()
        pedidos = self.servico.listar_por_usuario(usuario_id, limite, offset)
        return http.ok([p.to_dict() for p in pedidos], total=len(pedidos))

    def buscar(self, pedido_id: int):
        """GET /pedidos/<pedido_id> — próprio usuário ou administrador."""
        pedido = self.servico.buscar(pedido_id)

        usuario = usuario_atual()
        if not usuario.is_admin and pedido.usuario_id != usuario.id:
            # Mesma resposta de um pedido inexistente: confirmar a existência
            # de um pedido alheio já é informação demais.
            raise NotFoundError(f"Pedido {pedido_id} não encontrado.")

        return http.ok(pedido.to_dict())

    def atualizar_status(self, pedido_id: int):
        """PUT /pedidos/<pedido_id>/status — restrito a administradores."""
        novo_status = carregar_status(http.corpo_json())
        pedido = self.servico.atualizar_status(pedido_id, novo_status)
        return http.ok(pedido.to_dict(), mensagem="Status atualizado.")
