from flask import request, jsonify
from src.services.pedido_service import PedidoService
import logging

logger = logging.getLogger(__name__)

pedido_service = PedidoService()


class PedidoController:
    """Controller for order-related operations"""

    @staticmethod
    def criar_pedido():
        """POST /pedidos - Create new order"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            # In production, use request.current_user_id from JWT
            # For backward compatibility, allow usuario_id in request body
            usuario_id = dados.get('usuario_id')
            itens = dados.get('itens', [])

            if not usuario_id:
                return jsonify({'erro': 'Usuario ID é obrigatório'}), 400

            # Delegate to service (includes validation and transaction)
            pedido = pedido_service.criar_pedido(usuario_id, itens)

            return jsonify({
                'dados': pedido.to_dict(),
                'sucesso': True,
                'mensagem': 'Pedido criado com sucesso'
            }), 201

        except ValueError as e:
            # Business logic error
            return jsonify({'erro': str(e), 'sucesso': False}), 400

        except Exception as e:
            logger.error(f"Erro ao criar pedido: {e}")
            raise

    @staticmethod
    def listar_todos_pedidos():
        """GET /pedidos - List all orders (admin only in production)"""
        try:
            # Use eager loading to avoid N+1 queries
            pedidos = pedido_service.listar_todos_pedidos()

            return jsonify({
                'dados': [p.to_dict() for p in pedidos],
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao listar pedidos: {e}")
            raise

    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        """GET /pedidos/usuario/<id> - List user orders"""
        try:
            # Use eager loading to avoid N+1 queries
            pedidos = pedido_service.listar_pedidos_usuario(usuario_id)

            return jsonify({
                'dados': [p.to_dict() for p in pedidos],
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao listar pedidos do usuário: {e}")
            raise

    @staticmethod
    def atualizar_status_pedido(pedido_id):
        """PUT /pedidos/<id>/status - Update order status"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            novo_status = dados.get('status')

            if not novo_status:
                return jsonify({'erro': 'Status é obrigatório'}), 400

            # Delegate to service
            pedido = pedido_service.atualizar_status(pedido_id, novo_status)

            return jsonify({
                'dados': pedido.to_dict(),
                'sucesso': True,
                'mensagem': 'Status atualizado com sucesso'
            }), 200

        except ValueError as e:
            return jsonify({'erro': str(e)}), 400

        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            raise

    @staticmethod
    def relatorio_vendas():
        """GET /relatorios/vendas - Generate sales report"""
        try:
            relatorio = pedido_service.relatorio_vendas()

            return jsonify({
                'dados': relatorio,
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise

    @staticmethod
    def health_check():
        """GET /health - Health check endpoint (no sensitive data!)"""
        try:
            from src.config.database import db
            from src.models.produto import Produto
            from src.models.usuario import Usuario
            from src.models.pedido import Pedido

            # Test database connection
            db.session.execute(db.text("SELECT 1"))

            # Get counts
            produtos_count = Produto.query.count()
            usuarios_count = Usuario.query.count()
            pedidos_count = Pedido.query.count()

            return jsonify({
                'status': 'ok',
                'database': 'connected',
                'counts': {
                    'produtos': produtos_count,
                    'usuarios': usuarios_count,
                    'pedidos': pedidos_count
                },
                'version': '2.0.0'
                # NOTE: NO secret_key, NO debug flag, NO sensitive data!
            }), 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'error',
                'database': 'disconnected',
                'error': str(e)
            }), 503
