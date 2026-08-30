"""Model Task — entidade + a regra `is_overdue`, que é intrínseca ao registro.

A serialização saiu daqui para `schemas/task_schema.py`; antes existiam quatro
implementações divergentes da mesma lógica de `overdue`.
"""
from datetime import datetime

from src.config.constants import (
    DEFAULT_PRIORITY,
    MAX_TAGS_LENGTH,
    MAX_TITLE_LENGTH,
    TaskStatus,
)
from src.config.database import db

TAG_SEPARATOR = ','


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(MAX_TITLE_LENGTH), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50), nullable=False, default=TaskStatus.PENDING.value, index=True
    )
    priority = db.Column(db.Integer, nullable=False, default=DEFAULT_PRIORITY, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    tags = db.Column(db.String(MAX_TAGS_LENGTH), nullable=True)

    user = db.relationship('User', backref=db.backref('tasks', passive_deletes=True))
    category = db.relationship('Category', backref=db.backref('tasks', passive_deletes=True))

    __table_args__ = (
        db.CheckConstraint(
            'priority BETWEEN 1 AND 5', name='ck_tasks_priority_range'
        ),
        db.CheckConstraint(
            "status IN ('pending', 'in_progress', 'done', 'cancelled')",
            name='ck_tasks_status_valid',
        ),
    )

    @property
    def tag_list(self) -> list[str]:
        if not self.tags:
            return []
        return [tag for tag in (t.strip() for t in self.tags.split(TAG_SEPARATOR)) if tag]

    @property
    def is_overdue(self) -> bool:
        """True se a task venceu e ainda está aberta. Fonte única desta regra."""
        if not self.due_date:
            return False
        if self.status in TaskStatus.closed():
            return False
        return self.due_date < datetime.utcnow()

    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days

    def __repr__(self) -> str:
        return f'<Task {self.id} {self.title!r}>'
