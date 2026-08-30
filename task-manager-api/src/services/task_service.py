"""Regras de negócio de tasks. Sem dependência de Flask/HTTP."""
import logging

from src.config.constants import TaskStatus
from src.config.database import db
from src.models.task import TAG_SEPARATOR, Task
from src.repositories.category_repository import CategoryRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.utils.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
        category_repository: CategoryRepository | None = None,
    ) -> None:
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()
        self.category_repository = category_repository or CategoryRepository()

    def list_tasks(self) -> list[Task]:
        return self.task_repository.list_all()

    def get_task(self, task_id: int) -> Task:
        task = self.task_repository.find_by_id(task_id)
        if task is None:
            raise NotFoundError('Task não encontrada')
        return task

    def search_tasks(self, filters: dict) -> list[Task]:
        return self.task_repository.search(
            term=filters.get('q'),
            status=filters.get('status'),
            priority=filters.get('priority'),
            user_id=filters.get('user_id'),
        )

    def create_task(self, data: dict) -> Task:
        self._assert_relations_exist(data.get('user_id'), data.get('category_id'))

        task = Task(
            title=data['title'],
            description=data.get('description') or '',
            status=data['status'],
            priority=data['priority'],
            user_id=data.get('user_id'),
            category_id=data.get('category_id'),
            due_date=data.get('due_date'),
            tags=self._join_tags(data.get('tags')),
        )

        self.task_repository.add(task)
        db.session.commit()
        logger.info('Task criada: id=%s title=%r', task.id, task.title)
        return task

    def update_task(self, task_id: int, data: dict) -> Task:
        task = self.get_task(task_id)

        self._assert_relations_exist(
            data.get('user_id') if 'user_id' in data else None,
            data.get('category_id') if 'category_id' in data else None,
        )

        for field in ('title', 'description', 'status', 'priority', 'user_id',
                      'category_id', 'due_date'):
            if field in data:
                setattr(task, field, data[field])

        if 'tags' in data:
            task.tags = self._join_tags(data['tags'])

        db.session.commit()
        logger.info('Task atualizada: id=%s', task.id)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.task_repository.delete(task)
        db.session.commit()
        logger.info('Task deletada: id=%s', task_id)

    def get_stats(self) -> dict:
        """Estatísticas globais — agregações no banco, não em Python."""
        total = self.task_repository.count()
        by_status = self.task_repository.count_by_status()
        done = by_status[TaskStatus.DONE.value]

        return {
            'total': total,
            'pending': by_status[TaskStatus.PENDING.value],
            'in_progress': by_status[TaskStatus.IN_PROGRESS.value],
            'done': done,
            'cancelled': by_status[TaskStatus.CANCELLED.value],
            'overdue': len(self.task_repository.list_overdue()),
            'completion_rate': self.completion_rate(done, total),
        }

    @staticmethod
    def completion_rate(completed: int, total: int) -> float:
        """Percentual de conclusão. Regra centralizada, antes duplicada 3x."""
        if total <= 0:
            return 0
        return round((completed / total) * 100, 2)

    def _assert_relations_exist(self, user_id: int | None, category_id: int | None) -> None:
        """Valida FKs antes de gravar, para não criar registros órfãos."""
        if user_id is not None and self.user_repository.find_by_id(user_id) is None:
            raise NotFoundError('Usuário não encontrado')
        if category_id is not None and self.category_repository.find_by_id(category_id) is None:
            raise NotFoundError('Categoria não encontrada')

    @staticmethod
    def _join_tags(tags) -> str | None:
        if tags is None:
            return None
        if isinstance(tags, str):
            tags = tags.split(TAG_SEPARATOR)
        cleaned = [tag.strip() for tag in tags if tag and tag.strip()]
        return TAG_SEPARATOR.join(cleaned) if cleaned else None
