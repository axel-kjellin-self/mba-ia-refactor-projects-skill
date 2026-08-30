"""Regras de negócio de categorias. Sem dependência de Flask/HTTP."""
import logging

from src.config.database import db
from src.models.category import Category
from src.repositories.category_repository import CategoryRepository
from src.repositories.task_repository import TaskRepository
from src.utils.exceptions import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(
        self,
        category_repository: CategoryRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        self.category_repository = category_repository or CategoryRepository()
        self.task_repository = task_repository or TaskRepository()

    def list_categories(self) -> list[tuple[Category, int]]:
        """Categorias + contagem de tasks. Duas queries no total, não 1+N."""
        categories = self.category_repository.list_all()
        counts = self.task_repository.count_by_category()
        return [(category, counts.get(category.id, 0)) for category in categories]

    def get_category(self, category_id: int) -> Category:
        category = self.category_repository.find_by_id(category_id)
        if category is None:
            raise NotFoundError('Categoria não encontrada')
        return category

    def create_category(self, data: dict) -> Category:
        if self.category_repository.exists_name(data['name']):
            raise ConflictError('Categoria já existe')

        category = Category(
            name=data['name'],
            description=data.get('description') or '',
            color=data['color'],
        )
        self.category_repository.add(category)
        db.session.commit()
        logger.info('Categoria criada: id=%s name=%r', category.id, category.name)
        return category

    def update_category(self, category_id: int, data: dict) -> Category:
        category = self.get_category(category_id)

        if 'name' in data and self.category_repository.exists_name(
            data['name'], exclude_id=category_id
        ):
            raise ConflictError('Categoria já existe')

        for field in ('name', 'description', 'color'):
            if field in data:
                setattr(category, field, data[field])

        db.session.commit()
        logger.info('Categoria atualizada: id=%s', category.id)
        return category

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        self.category_repository.delete(category)
        db.session.commit()
        logger.info('Categoria deletada: id=%s', category_id)
