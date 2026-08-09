from src.models.user import User
from src.models.task import Task
from src.config.database import db
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User business logic"""

    @staticmethod
    def get_all_users():
        """Get all users with task count"""
        users = User.query.all()
        return [user.to_dict() for user in users]

    @staticmethod
    def get_user_by_id(user_id, include_tasks=False):
        """Get user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    @staticmethod
    def create_user(data):
        """
        Create new user

        Args:
            data: dict with name, email, password, role

        Returns:
            Created User object

        Raises:
            ValueError: If validation fails
        """
        # Check if email already exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            raise ValueError("Email already registered")

        user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User created: {user.id} - {user.name}")
            return user

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise

    @staticmethod
    def update_user(user_id, data):
        """Update user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check email uniqueness if being updated
        if 'email' in data:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ValueError("Email already registered")

        # Update fields
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        if 'role' in data:
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']

        try:
            db.session.commit()
            logger.info(f"User updated: {user.id}")
            return user

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {e}", exc_info=True)
            raise

    @staticmethod
    def delete_user(user_id):
        """
        Delete user and all associated tasks

        WARNING: This is a destructive operation
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Delete all tasks associated with this user
        tasks = Task.query.filter_by(user_id=user_id).all()
        for task in tasks:
            db.session.delete(task)

        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User deleted: {user_id} (with {len(tasks)} tasks)")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {e}", exc_info=True)
            raise

    @staticmethod
    def get_user_tasks(user_id):
        """Get all tasks for a user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        tasks = Task.query.filter_by(user_id=user_id).all()
        return tasks
