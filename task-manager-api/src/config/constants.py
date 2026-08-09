# Validation Constants
class ValidationRules:
    # Task
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    # User
    MIN_PASSWORD_LENGTH = 8  # Increased from 4
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 150

    # Category
    MAX_CATEGORY_NAME_LENGTH = 100
    MAX_CATEGORY_DESC_LENGTH = 300

    # Valid Values
    VALID_TASK_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
    VALID_USER_ROLES = ['user', 'admin', 'manager']


# Default Values
class Defaults:
    TASK_STATUS = 'pending'
    TASK_PRIORITY = 3
    USER_ROLE = 'user'
    USER_ACTIVE = True
    CATEGORY_COLOR = '#000000'


# Date Formats
class DateFormats:
    ISO_DATE = '%Y-%m-%d'
    ISO_DATETIME = '%Y-%m-%d %H:%M:%S'
    DISPLAY_DATE = '%d/%m/%Y'


# Priority Labels
PRIORITY_LABELS = {
    1: 'Critical',
    2: 'High',
    3: 'Medium',
    4: 'Low',
    5: 'Minimal'
}


# Status Labels
STATUS_LABELS = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'done': 'Done',
    'cancelled': 'Cancelled'
}
