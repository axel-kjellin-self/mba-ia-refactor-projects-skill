"""Constantes de domínio — fonte única de verdade.

Antes estas regras estavam espalhadas como literais em 12+ pontos das rotas
(finding LOW: Magic Numbers) e duplicadas em `utils/helpers.py`, onde eram
definidas mas nunca importadas.
"""
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]

    @classmethod
    def closed(cls) -> set[str]:
        """Status que encerram a task — não podem ficar atrasadas."""
        return {cls.DONE.value, cls.CANCELLED.value}


class UserRole(StrEnum):
    USER = 'user'
    ADMIN = 'admin'
    MANAGER = 'manager'

    @classmethod
    def values(cls) -> list[str]:
        return [role.value for role in cls]


# Task
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
MAX_TAGS_LENGTH = 500
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_THRESHOLD = 2  # priority <= 2 é considerada alta

PRIORITY_LABELS: dict[int, str] = {
    1: 'critical',
    2: 'high',
    3: 'medium',
    4: 'low',
    5: 'minimal',
}

# User
MIN_PASSWORD_LENGTH = 12
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 150

# Category
MAX_CATEGORY_NAME_LENGTH = 100
MAX_CATEGORY_DESCRIPTION_LENGTH = 300
DEFAULT_COLOR = '#000000'
HEX_COLOR_PATTERN = r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'

# Reports
RECENT_ACTIVITY_DAYS = 7

# Datas
DATE_FORMAT = '%Y-%m-%d'
