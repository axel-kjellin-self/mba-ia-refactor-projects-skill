from src.config.database import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default='#000000')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_task_count=False):
        """Serialize category to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_task_count:
            data['task_count'] = len(self.tasks)

        return data
