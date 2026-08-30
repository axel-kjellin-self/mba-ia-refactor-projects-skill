"""Acesso a dados de User. Sem regras de negócio, sem HTTP."""
from sqlalchemy import func

from src.config.database import db
from src.models.task import Task
from src.models.user import User


class UserRepository:
    @staticmethod
    def find_by_id(user_id: int) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def find_by_email(email: str) -> User | None:
        return db.session.query(User).filter_by(email=email).first()

    @staticmethod
    def list_all() -> list[User]:
        return db.session.query(User).order_by(User.id).all()

    @staticmethod
    def list_all_with_task_counts() -> list[tuple[User, int]]:
        """Usuários + contagem de tasks em UMA query (antes era N+1 via `len(u.tasks)`)."""
        rows = (
            db.session.query(User, func.count(Task.id))
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id)
            .order_by(User.id)
            .all()
        )
        return [(user, count) for user, count in rows]

    @staticmethod
    def count() -> int:
        return db.session.query(func.count(User.id)).scalar() or 0

    @staticmethod
    def exists_email(email: str, exclude_id: int | None = None) -> bool:
        query = db.session.query(User.id).filter(User.email == email)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return db.session.query(query.exists()).scalar()

    @staticmethod
    def add(user: User) -> User:
        db.session.add(user)
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
