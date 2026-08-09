from datetime import datetime
from src.config.database import db
from src.config.constants import PedidoStatus


class Pedido(db.Model):
    """Order model"""
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete='CASCADE'),
        nullable=False
    )
    status = db.Column(db.String(20), default=PedidoStatus.PENDENTE, nullable=False)
    total = db.Column(db.Float, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships with eager loading to avoid N+1 queries
    itens = db.relationship(
        'ItemPedido',
        backref='pedido',
        lazy='joined',
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_items=True):
        """Convert order to dictionary"""
        data = {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'status': self.status,
            'total': self.total,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

        if include_items:
            data['itens'] = [item.to_dict() for item in self.itens]

        return data

    def __repr__(self):
        return f'<Pedido {self.id}>'


class ItemPedido(db.Model):
    """Order item model"""
    __tablename__ = 'itens_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedidos.id', ondelete='CASCADE'),
        nullable=False
    )
    produto_id = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id', ondelete='RESTRICT'),
        nullable=False
    )
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'produto_nome': self.produto.nome if self.produto else 'Desconhecido',
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
            'subtotal': self.quantidade * self.preco_unitario
        }

    def __repr__(self):
        return f'<ItemPedido {self.id}>'
