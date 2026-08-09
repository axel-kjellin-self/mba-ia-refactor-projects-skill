from src.config.database import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending', index=True)
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    # Relationships
    category = db.relationship('Category', backref='tasks')

    @property
    def is_overdue(self):
        """
        Check if task is overdue
        Centralized logic to avoid duplication
        """
        if not self.due_date:
            return False

        if self.due_date < datetime.utcnow():
            if self.status not in ['done', 'cancelled']:
                return True

        return False

    def validate_status(self, new_status):
        """Validate task status"""
        from src.config.constants import ValidationRules
        return new_status in ValidationRules.VALID_TASK_STATUSES

    def validate_priority(self, p):
        """Validate task priority"""
        from src.config.constants import ValidationRules
        return ValidationRules.MIN_PRIORITY <= p <= ValidationRules.MAX_PRIORITY

    def to_dict(self, include_overdue=True):
        """Serialize task to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else []
        }

        if include_overdue:
            data['overdue'] = self.is_overdue

        return data
