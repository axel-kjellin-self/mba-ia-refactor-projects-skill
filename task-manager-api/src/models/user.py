from src.config.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships with eager loading
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def set_password(self, pwd):
        """Hash password using bcrypt (via werkzeug)"""
        self.password = generate_password_hash(pwd, method='pbkdf2:sha256')

    def check_password(self, pwd):
        """Verify password against hash"""
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def to_dict(self, include_tasks=False):
        """
        Serialize user to dictionary
        NEVER includes password hash
        """
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_tasks:
            data['tasks'] = [task.to_dict() for task in self.tasks]
            data['task_count'] = self.tasks.count()
        else:
            data['task_count'] = self.tasks.count()

        return data
