"""Model User — apenas definição de entidade e hashing de senha."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from src.config.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH, UserRole
from src.config.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    email = db.Column(db.String(MAX_EMAIL_LENGTH), unique=True, nullable=False, index=True)
    # Armazena o hash (scrypt, default do Werkzeug), nunca a senha em claro.
    password_hash = db.Column('password', db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=UserRole.USER.value)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        """Gera hash com salt via Werkzeug (substitui o MD5 sem salt anterior)."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    def __repr__(self) -> str:
        return f'<User {self.id} {self.email}>'
