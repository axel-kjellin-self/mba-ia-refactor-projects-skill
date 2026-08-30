"""Acesso a dados de Task. Sem regras de negócio, sem HTTP."""
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from src.config.constants import TaskStatus
from src.config.database import db
from src.models.task import Task


def _escape_like(term: str) -> str:
    """Escapa os curingas do LIKE para que `%` e `_` do usuário sejam literais."""
    return term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


class TaskRepository:
    @staticmethod
    def find_by_id(task_id: int) -> Task | None:
        return db.session.get(Task, task_id)

    @staticmethod
    def list_all() -> list[Task]:
        """Carrega user e category junto — elimina o N+1 do antigo `GET /tasks`."""
        return (
            db.session.query(Task)
            .options(joinedload(Task.user), joinedload(Task.category))
            .order_by(Task.id)
            .all()
        )

    @staticmethod
    def list_by_user(user_id: int) -> list[Task]:
        return (
            db.session.query(Task)
            .options(joinedload(Task.category))
            .filter(Task.user_id == user_id)
            .order_by(Task.id)
            .all()
        )

    @staticmethod
    def search(
        term: str | None = None,
        status: str | None = None,
        priority: int | None = None,
        user_id: int | None = None,
    ) -> list[Task]:
        query = db.session.query(Task).options(
            joinedload(Task.user), joinedload(Task.category)
        )

        if term:
            pattern = f'%{_escape_like(term)}%'
            query = query.filter(
                or_(
                    Task.title.like(pattern, escape='\\'),
                    Task.description.like(pattern, escape='\\'),
                )
            )
        if status:
            query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if user_id is not None:
            query = query.filter(Task.user_id == user_id)

        return query.order_by(Task.id).all()

    @staticmethod
    def count() -> int:
        return db.session.query(func.count(Task.id)).scalar() or 0

    @staticmethod
    def count_by_status() -> dict[str, int]:
        """Uma query agregada no lugar de quatro `count()` separados."""
        rows = db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        counts = {status: 0 for status in TaskStatus.values()}
        counts.update({status: count for status, count in rows})
        return counts

    @staticmethod
    def count_by_priority() -> dict[int, int]:
        """Uma query agregada no lugar de cinco `count()` separados."""
        rows = db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
        counts = {priority: 0 for priority in range(1, 6)}
        counts.update({priority: count for priority, count in rows})
        return counts

    @staticmethod
    def list_overdue() -> list[Task]:
        """Filtra no banco em vez de varrer todas as tasks em Python."""
        return (
            db.session.query(Task)
            .filter(
                Task.due_date.isnot(None),
                Task.due_date < datetime.utcnow(),
                Task.status.notin_(list(TaskStatus.closed())),
            )
            .order_by(Task.due_date)
            .all()
        )

    @staticmethod
    def count_created_since(since: datetime) -> int:
        return (
            db.session.query(func.count(Task.id)).filter(Task.created_at >= since).scalar() or 0
        )

    @staticmethod
    def count_completed_since(since: datetime) -> int:
        return (
            db.session.query(func.count(Task.id))
            .filter(Task.status == TaskStatus.DONE.value, Task.updated_at >= since)
            .scalar()
            or 0
        )

    @staticmethod
    def count_by_user_and_status() -> dict[int, dict[str, int]]:
        """Matriz user_id -> {status: count} em UMA query.

        Substitui o loop `for u in users: Task.query.filter_by(user_id=u.id)`.
        """
        rows = (
            db.session.query(Task.user_id, Task.status, func.count(Task.id))
            .group_by(Task.user_id, Task.status)
            .all()
        )
        result: dict[int, dict[str, int]] = {}
        for user_id, status, count in rows:
            if user_id is None:
                continue
            result.setdefault(user_id, {})[status] = count
        return result

    @staticmethod
    def count_by_category() -> dict[int, int]:
        """category_id -> total de tasks, em UMA query."""
        rows = (
            db.session.query(Task.category_id, func.count(Task.id))
            .filter(Task.category_id.isnot(None))
            .group_by(Task.category_id)
            .all()
        )
        return {category_id: count for category_id, count in rows}

    @staticmethod
    def add(task: Task) -> Task:
        db.session.add(task)
        return task

    @staticmethod
    def delete(task: Task) -> None:
        db.session.delete(task)

    @staticmethod
    def delete_by_user(user_id: int) -> int:
        return (
            db.session.query(Task)
            .filter(Task.user_id == user_id)
            .delete(synchronize_session=False)
        )
