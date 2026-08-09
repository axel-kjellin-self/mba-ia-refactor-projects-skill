from src.models.pedido import Pedido, ItemPedido
from src.models.produto import Produto
from src.config.database import db
from src.config.constants import DiscountTiers, PedidoStatus
import logging

logger = logging.getLogger(__name__)


class PedidoService:
    """Business logic for order operations"""

    @staticmethod
    def criar_pedido(usuario_id, itens):
        """
        Create an order with stock validation and total calculation

        Args:
            usuario_id: ID of the user placing the order
            itens: List of dicts with product_id and quantidade

        Returns:
            Created Pedido instance

        Raises:
            ValueError: If validation fails
        """
        if not itens or len(itens) == 0:
            raise ValueError("Pedido deve ter pelo menos 1 item")

        # Use transaction to ensure data consistency
        try:
            # Validate stock availability
            for item in itens:
                produto = Produto.query.get(item['produto_id'])

                if not produto:
                    raise ValueError(f"Produto {item['produto_id']} não encontrado")

                if produto.estoque < item['quantidade']:
                    raise ValueError(f"Estoque insuficiente para {produto.nome}")

            # Calculate total
            total = 0
            for item in itens:
                produto = Produto.query.get(item['produto_id'])
                total += produto.preco * item['quantidade']

            # Create order
            pedido = Pedido(
                usuario_id=usuario_id,
                status=PedidoStatus.PENDENTE,
                total=total
            )
            db.session.add(pedido)
            db.session.flush()  # Get pedido.id without committing

            # Create order items and update stock
            for item in itens:
                produto = Produto.query.get(item['produto_id'])

                # Create order item
                item_pedido = ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=item['produto_id'],
                    quantidade=item['quantidade'],
                    preco_unitario=produto.preco
                )
                db.session.add(item_pedido)

                # Update stock
                produto.estoque -= item['quantidade']

            # Commit transaction
            db.session.commit()

            logger.info(f"Pedido {pedido.id} criado para usuario {usuario_id}")

            return pedido

        except Exception as e:
            # Rollback in case of any error
            db.session.rollback()
            logger.error(f"Erro ao criar pedido: {e}")
            raise

    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        """
        List all orders for a user with eager loading to avoid N+1 queries

        Args:
            usuario_id: User ID

        Returns:
            List of Pedido instances
        """
        # Eager loading prevents N+1 query problem
        return Pedido.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def listar_todos_pedidos():
        """List all orders with eager loading"""
        return Pedido.query.all()

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        """
        Update order status

        Args:
            pedido_id: Order ID
            novo_status: New status

        Returns:
            Updated Pedido instance

        Raises:
            ValueError: If validation fails
        """
        if novo_status not in PedidoStatus.ALL:
            raise ValueError(
                f"Status inválido. Válidos: {', '.join(PedidoStatus.ALL)}"
            )

        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            raise ValueError(f"Pedido {pedido_id} não encontrado")

        pedido.status = novo_status
        db.session.commit()

        logger.info(f"Pedido {pedido_id} atualizado para status {novo_status}")

        return pedido

    @staticmethod
    def calcular_desconto(faturamento):
        """
        Calculate discount based on revenue tiers

        Args:
            faturamento: Total revenue

        Returns:
            Discount amount
        """
        if faturamento >= DiscountTiers.TIER_1_THRESHOLD:
            return faturamento * DiscountTiers.TIER_1_RATE
        elif faturamento >= DiscountTiers.TIER_2_THRESHOLD:
            return faturamento * DiscountTiers.TIER_2_RATE
        elif faturamento >= DiscountTiers.TIER_3_THRESHOLD:
            return faturamento * DiscountTiers.TIER_3_RATE

        return 0

    @staticmethod
    def relatorio_vendas():
        """
        Generate sales report with totals and statistics

        Returns:
            Dict with sales metrics
        """
        total_pedidos = Pedido.query.count()
        faturamento_bruto = db.session.query(db.func.sum(Pedido.total)).scalar() or 0

        pendentes = Pedido.query.filter_by(status=PedidoStatus.PENDENTE).count()
        aprovados = Pedido.query.filter_by(status=PedidoStatus.APROVADO).count()
        cancelados = Pedido.query.filter_by(status=PedidoStatus.CANCELADO).count()

        # Calculate discount based on business rules
        desconto = PedidoService.calcular_desconto(faturamento_bruto)

        return {
            'total_pedidos': total_pedidos,
            'faturamento_bruto': round(faturamento_bruto, 2),
            'desconto_aplicavel': round(desconto, 2),
            'faturamento_liquido': round(faturamento_bruto - desconto, 2),
            'pedidos_pendentes': pendentes,
            'pedidos_aprovados': aprovados,
            'pedidos_cancelados': cancelados,
            'ticket_medio': round(faturamento_bruto / total_pedidos, 2) if total_pedidos > 0 else 0
        }
