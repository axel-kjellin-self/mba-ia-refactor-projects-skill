from datetime import datetime
from src.config.database import db
from src.config.constants import CategoriaProduto


class Produto(db.Model):
    """Product model"""
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0, nullable=False)
    categoria = db.Column(db.String(50), default=CategoriaProduto.GERAL, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy='dynamic')

    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'estoque': self.estoque,
            'categoria': self.categoria,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

    def __repr__(self):
        return f'<Produto {self.nome}>'
