"""Acesso a dados de Category. Sem regras de negócio, sem HTTP."""
from sqlalchemy import func

from src.config.database import db
from src.models.category import Category


class CategoryRepository:
    @staticmethod
    def find_by_id(category_id: int) -> Category | None:
        return db.session.get(Category, category_id)

    @staticmethod
    def list_all() -> list[Category]:
        return db.session.query(Category).order_by(Category.id).all()

    @staticmethod
    def count() -> int:
        return db.session.query(func.count(Category.id)).scalar() or 0

    @staticmethod
    def exists_name(name: str, exclude_id: int | None = None) -> bool:
        query = db.session.query(Category.id).filter(Category.name == name)
        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)
        return db.session.query(query.exists()).scalar()

    @staticmethod
    def add(category: Category) -> Category:
        db.session.add(category)
        return category

    @staticmethod
    def delete(category: Category) -> None:
        db.session.delete(category)
