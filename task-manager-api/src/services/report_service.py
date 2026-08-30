"""Geração de relatórios.

Substitui a função `summary_report()` de 90 linhas e ~20 queries que vivia
dentro do route handler. Agora as agregações acontecem no banco.
"""
from datetime import datetime, timedelta

from src.config.constants import (
    HIGH_PRIORITY_THRESHOLD,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_DAYS,
    TaskStatus,
)
from src.repositories.category_repository import CategoryRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.services.task_service import TaskService
from src.utils.exceptions import NotFoundError


class ReportService:
    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
        category_repository: CategoryRepository | None = None,
    ) -> None:
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()
        self.category_repository = category_repository or CategoryRepository()

    def summary(self) -> dict:
        by_status = self.task_repository.count_by_status()
        by_priority = self.task_repository.count_by_priority()
        overdue_tasks = self.task_repository.list_overdue()
        since = datetime.utcnow() - timedelta(days=RECENT_ACTIVITY_DAYS)

        return {
            'generated_at': datetime.utcnow().isoformat(),
            'overview': {
                'total_tasks': self.task_repository.count(),
                'total_users': self.user_repository.count(),
                'total_categories': self.category_repository.count(),
            },
            'tasks_by_status': by_status,
            'tasks_by_priority': {
                PRIORITY_LABELS[priority]: count for priority, count in by_priority.items()
            },
            'overdue': {
                'count': len(overdue_tasks),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'due_date': task.due_date.isoformat(),
                        'days_overdue': task.days_overdue,
                    }
                    for task in overdue_tasks
                ],
            },
            'recent_activity': {
                f'tasks_created_last_{RECENT_ACTIVITY_DAYS}_days':
                    self.task_repository.count_created_since(since),
                f'tasks_completed_last_{RECENT_ACTIVITY_DAYS}_days':
                    self.task_repository.count_completed_since(since),
            },
            'user_productivity': self._user_productivity(),
        }

    def user_report(self, user_id: int) -> dict:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError('Usuário não encontrado')

        tasks = self.task_repository.list_by_user(user_id)
        counts = {status: 0 for status in TaskStatus.values()}
        overdue = 0
        high_priority = 0

        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
            if task.priority <= HIGH_PRIORITY_THRESHOLD:
                high_priority += 1
            if task.is_overdue:
                overdue += 1

        total = len(tasks)
        done = counts[TaskStatus.DONE.value]

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': counts[TaskStatus.PENDING.value],
                'in_progress': counts[TaskStatus.IN_PROGRESS.value],
                'cancelled': counts[TaskStatus.CANCELLED.value],
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': TaskService.completion_rate(done, total),
            },
        }

    def _user_productivity(self) -> list[dict]:
        """Produtividade por usuário — 2 queries, não 1+N."""
        matrix = self.task_repository.count_by_user_and_status()
        result = []
        for user in self.user_repository.list_all():
            statuses = matrix.get(user.id, {})
            total = sum(statuses.values())
            completed = statuses.get(TaskStatus.DONE.value, 0)
            result.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': TaskService.completion_rate(completed, total),
            })
        return result
