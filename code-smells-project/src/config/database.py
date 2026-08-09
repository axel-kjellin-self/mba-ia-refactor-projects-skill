from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)

    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from src.models.usuario import Usuario
        from src.models.produto import Produto
        from src.models.pedido import Pedido, ItemPedido

        # Create all tables
        db.create_all()

        # Seed initial data if database is empty
        _seed_data()


def _seed_data():
    """Seed database with initial data if empty"""
    from src.models.usuario import Usuario
    from src.models.produto import Produto

    # Check if data already exists
    if Usuario.query.first() is None:
        # Create admin user
        admin = Usuario(
            nome='Admin',
            email='admin@loja.com',
            tipo='admin'
        )
        admin.set_password('admin123')

        # Create sample users
        joao = Usuario(
            nome='João Silva',
            email='joao@email.com',
            tipo='cliente'
        )
        joao.set_password('senha_segura_joao')

        maria = Usuario(
            nome='Maria Santos',
            email='maria@email.com',
            tipo='cliente'
        )
        maria.set_password('senha_segura_maria')

        db.session.add_all([admin, joao, maria])
        db.session.commit()

        print("✓ Users seeded")

    if Produto.query.first() is None:
        # Create sample products
        produtos = [
            Produto(
                nome="Notebook Gamer",
                descricao="Notebook potente para jogos",
                preco=5999.99,
                estoque=10,
                categoria="informatica"
            ),
            Produto(
                nome="Mouse Wireless",
                descricao="Mouse sem fio ergonômico",
                preco=89.90,
                estoque=50,
                categoria="informatica"
            ),
            Produto(
                nome="Teclado Mecânico",
                descricao="Teclado mecânico RGB",
                preco=299.90,
                estoque=30,
                categoria="informatica"
            ),
            Produto(
                nome="Monitor 27''",
                descricao="Monitor 27 polegadas 144hz",
                preco=1899.90,
                estoque=15,
                categoria="informatica"
            ),
            Produto(
                nome="Headset Gamer",
                descricao="Headset com microfone",
                preco=199.90,
                estoque=25,
                categoria="informatica"
            ),
            Produto(
                nome="Cadeira Gamer",
                descricao="Cadeira ergonômica",
                preco=1299.90,
                estoque=8,
                categoria="moveis"
            ),
            Produto(
                nome="Webcam HD",
                descricao="Webcam 1080p",
                preco=249.90,
                estoque=20,
                categoria="informatica"
            ),
            Produto(
                nome="Hub USB",
                descricao="Hub USB 3.0 7 portas",
                preco=79.90,
                estoque=40,
                categoria="informatica"
            ),
            Produto(
                nome="SSD 1TB",
                descricao="SSD NVMe 1TB",
                preco=449.90,
                estoque=35,
                categoria="informatica"
            ),
            Produto(
                nome="Camiseta Dev",
                descricao="Camiseta estampa código",
                preco=59.90,
                estoque=100,
                categoria="vestuario"
            ),
        ]

        db.session.add_all(produtos)
        db.session.commit()

        print("✓ Products seeded")
