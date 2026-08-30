"""Regras de negócio de usuários. Sem dependência de Flask/HTTP."""
import logging

from src.config.database import db
from src.models.user import User
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.utils.exceptions import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.task_repository = task_repository or TaskRepository()

    def list_users(self) -> list[tuple[User, int]]:
        """Devolve pares (usuário, total de tasks) — uma única query agregada."""
        return self.user_repository.list_all_with_task_counts()

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError('Usuário não encontrado')
        return user

    def get_user_tasks(self, user_id: int):
        self.get_user(user_id)  # garante 404 se o usuário não existir
        return self.task_repository.list_by_user(user_id)

    def create_user(self, data: dict) -> User:
        if self.user_repository.exists_email(data['email']):
            raise ConflictError('Email já cadastrado')

        user = User(name=data['name'], email=data['email'], role=data['role'])
        user.set_password(data['password'])

        self.user_repository.add(user)
        db.session.commit()
        logger.info('Usuário criado: id=%s email=%s', user.id, user.email)
        return user

    def update_user(self, user_id: int, data: dict) -> User:
        user = self.get_user(user_id)

        if 'email' in data and self.user_repository.exists_email(
            data['email'], exclude_id=user_id
        ):
            raise ConflictError('Email já cadastrado')

        for field in ('name', 'email', 'role', 'active'):
            if field in data:
                setattr(user, field, data[field])

        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        logger.info('Usuário atualizado: id=%s', user.id)
        return user

    def delete_user(self, user_id: int) -> None:
        """Remove o usuário e suas tasks numa única transação.

        Antes o loop de deleção de tasks ficava fora do try/except, deixando a
        sessão suja quando falhava.
        """
        user = self.get_user(user_id)
        try:
            deleted = self.task_repository.delete_by_user(user_id)
            self.user_repository.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        logger.info('Usuário deletado: id=%s (%s tasks removidas)', user_id, deleted)
