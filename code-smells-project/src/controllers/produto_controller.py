from flask import request, jsonify
from src.services.produto_service import ProdutoService
import logging

logger = logging.getLogger(__name__)

produto_service = ProdutoService()


class ProdutoController:
    """Controller for product-related operations"""

    @staticmethod
    def listar_produtos():
        """GET /produtos - List all products"""
        try:
            produtos = produto_service.listar_todos()

            logger.info(f"Listando {len(produtos)} produtos")

            return jsonify({
                'dados': [p.to_dict() for p in produtos],
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao listar produtos: {e}")
            raise

    @staticmethod
    def buscar_produto(produto_id):
        """GET /produtos/<id> - Get product by ID"""
        try:
            produto = produto_service.buscar_por_id(produto_id)

            if not produto:
                return jsonify({
                    'erro': 'Produto não encontrado',
                    'sucesso': False
                }), 404

            return jsonify({
                'dados': produto.to_dict(),
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao buscar produto: {e}")
            raise

    @staticmethod
    def criar_produto():
        """POST /produtos - Create new product"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            nome = dados.get('nome')
            descricao = dados.get('descricao', '')
            preco = dados.get('preco')
            estoque = dados.get('estoque')
            categoria = dados.get('categoria', 'geral')

            # Validate required fields
            if not nome:
                return jsonify({'erro': 'Nome é obrigatório'}), 400
            if preco is None:
                return jsonify({'erro': 'Preço é obrigatório'}), 400
            if estoque is None:
                return jsonify({'erro': 'Estoque é obrigatório'}), 400

            # Delegate to service (includes validation)
            produto = produto_service.criar_produto(
                nome, descricao, preco, estoque, categoria
            )

            logger.info(f"Produto criado: {produto.nome} (ID: {produto.id})")

            return jsonify({
                'dados': produto.to_dict(),
                'sucesso': True,
                'mensagem': 'Produto criado com sucesso'
            }), 201

        except ValueError as e:
            # Business logic error
            return jsonify({'erro': str(e)}), 400

        except Exception as e:
            logger.error(f"Erro ao criar produto: {e}")
            raise

    @staticmethod
    def atualizar_produto(produto_id):
        """PUT /produtos/<id> - Update product"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            nome = dados.get('nome')
            descricao = dados.get('descricao', '')
            preco = dados.get('preco')
            estoque = dados.get('estoque')
            categoria = dados.get('categoria', 'geral')

            # Validate required fields
            if not nome:
                return jsonify({'erro': 'Nome é obrigatório'}), 400
            if preco is None:
                return jsonify({'erro': 'Preço é obrigatório'}), 400
            if estoque is None:
                return jsonify({'erro': 'Estoque é obrigatório'}), 400

            # Delegate to service
            produto = produto_service.atualizar_produto(
                produto_id, nome, descricao, preco, estoque, categoria
            )

            logger.info(f"Produto atualizado: {produto.nome} (ID: {produto.id})")

            return jsonify({
                'dados': produto.to_dict(),
                'sucesso': True,
                'mensagem': 'Produto atualizado com sucesso'
            }), 200

        except ValueError as e:
            return jsonify({'erro': str(e)}), 400

        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {e}")
            raise

    @staticmethod
    def deletar_produto(produto_id):
        """DELETE /produtos/<id> - Delete product"""
        try:
            produto_service.deletar_produto(produto_id)

            logger.info(f"Produto deletado: ID {produto_id}")

            return jsonify({
                'sucesso': True,
                'mensagem': 'Produto deletado com sucesso'
            }), 200

        except ValueError as e:
            return jsonify({'erro': str(e)}), 404

        except Exception as e:
            logger.error(f"Erro ao deletar produto: {e}")
            raise

    @staticmethod
    def buscar_produtos():
        """GET /produtos/busca - Search products with filters"""
        try:
            termo = request.args.get('q', '')
            categoria = request.args.get('categoria')
            preco_min = request.args.get('preco_min')
            preco_max = request.args.get('preco_max')

            # Validate price inputs
            try:
                if preco_min:
                    preco_min = float(preco_min)
                if preco_max:
                    preco_max = float(preco_max)
            except ValueError:
                return jsonify({'erro': 'Preços devem ser números válidos'}), 400

            # Delegate to service
            resultados = produto_service.buscar_produtos(
                termo, categoria, preco_min, preco_max
            )

            return jsonify({
                'dados': [p.to_dict() for p in resultados],
                'total': len(resultados),
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {e}")
            raise
