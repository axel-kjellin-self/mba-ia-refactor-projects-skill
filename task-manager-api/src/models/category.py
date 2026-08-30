"""Model Category — apenas definição de entidade."""
from datetime import datetime

from src.config.constants import (
    DEFAULT_COLOR,
    MAX_CATEGORY_DESCRIPTION_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
)
from src.config.database import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False)
    description = db.Column(db.String(MAX_CATEGORY_DESCRIPTION_LENGTH), nullable=True)
    color = db.Column(db.String(7), nullable=False, default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Category {self.id} {self.name}>'
