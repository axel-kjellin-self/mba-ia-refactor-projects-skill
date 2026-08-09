from src.models.produto import Produto
from src.config.database import db
from src.config.constants import ValidationRules, CategoriaProduto


class ProdutoService:
    """Business logic for product operations"""

    @staticmethod
    def criar_produto(nome, descricao, preco, estoque, categoria='geral'):
        """
        Create a new product with validation

        Args:
            nome: Product name
            descricao: Product description
            preco: Product price
            estoque: Stock quantity
            categoria: Product category

        Returns:
            Created Produto instance

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not nome:
            raise ValueError("Nome é obrigatório")

        if preco < 0:
            raise ValueError("Preço não pode ser negativo")

        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")

        if len(nome) < ValidationRules.MIN_PRODUCT_NAME_LENGTH:
            raise ValueError(
                f"Nome muito curto (mínimo {ValidationRules.MIN_PRODUCT_NAME_LENGTH} caracteres)"
            )

        if len(nome) > ValidationRules.MAX_PRODUCT_NAME_LENGTH:
            raise ValueError(
                f"Nome muito longo (máximo {ValidationRules.MAX_PRODUCT_NAME_LENGTH} caracteres)"
            )

        if categoria not in CategoriaProduto.ALL:
            raise ValueError(
                f"Categoria inválida. Válidas: {', '.join(CategoriaProduto.ALL)}"
            )

        # Create product
        produto = Produto(
            nome=nome,
            descricao=descricao or '',
            preco=preco,
            estoque=estoque,
            categoria=categoria
        )

        db.session.add(produto)
        db.session.commit()

        return produto

    @staticmethod
    def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
        """Update an existing product"""
        produto = Produto.query.get(produto_id)

        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado")

        # Same validations as create
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")

        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")

        if len(nome) < ValidationRules.MIN_PRODUCT_NAME_LENGTH:
            raise ValueError("Nome muito curto")

        if len(nome) > ValidationRules.MAX_PRODUCT_NAME_LENGTH:
            raise ValueError("Nome muito longo")

        if categoria not in CategoriaProduto.ALL:
            raise ValueError(f"Categoria inválida")

        # Update fields
        produto.nome = nome
        produto.descricao = descricao or ''
        produto.preco = preco
        produto.estoque = estoque
        produto.categoria = categoria

        db.session.commit()

        return produto

    @staticmethod
    def deletar_produto(produto_id):
        """Delete a product"""
        produto = Produto.query.get(produto_id)

        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado")

        db.session.delete(produto)
        db.session.commit()

        return True

    @staticmethod
    def buscar_por_id(produto_id):
        """Find product by ID"""
        return Produto.query.get(produto_id)

    @staticmethod
    def listar_todos():
        """List all active products"""
        return Produto.query.filter_by(ativo=True).all()

    @staticmethod
    def buscar_produtos(termo=None, categoria=None, preco_min=None, preco_max=None):
        """
        Search products with filters

        Args:
            termo: Search term (searches in name and description)
            categoria: Filter by category
            preco_min: Minimum price
            preco_max: Maximum price

        Returns:
            List of matching products
        """
        query = Produto.query.filter_by(ativo=True)

        if termo:
            # SAFE: Using ORM prevents SQL injection
            search_filter = f"%{termo}%"
            query = query.filter(
                (Produto.nome.ilike(search_filter)) |
                (Produto.descricao.ilike(search_filter))
            )

        if categoria:
            query = query.filter_by(categoria=categoria)

        if preco_min is not None:
            query = query.filter(Produto.preco >= preco_min)

        if preco_max is not None:
            query = query.filter(Produto.preco <= preco_max)

        return query.all()
