from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.config.database import db
from src.config.constants import UsuarioTipo


class Usuario(db.Model):
    """User model with secure password hashing"""
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default=UsuarioTipo.CLIENTE, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    pedidos = db.relationship('Pedido', backref='usuario', lazy='dynamic')

    def set_password(self, password):
        """Hash password using bcrypt"""
        self.senha = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.senha, password)

    def to_dict(self, include_password=False):
        """Convert user to dictionary - NEVER include password by default"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
        # Only include password if explicitly requested (should never be in API responses!)
        if include_password:
            data['senha'] = self.senha
        return data

    def __repr__(self):
        return f'<Usuario {self.email}>'
