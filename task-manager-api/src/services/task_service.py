from src.models.task import Task
from src.models.user import User
from src.models.category import Category
from src.config.database import db
from datetime import datetime
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Task business logic"""

    @staticmethod
    def get_all_tasks():
        """
        Get all tasks with eager loading to avoid N+1
        """
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category)
        ).all()

        result = []
        for task in tasks:
            task_data = task.to_dict()

            # Add user info if exists
            if task.user:
                task_data['user_name'] = task.user.name
            else:
                task_data['user_name'] = None

            # Add category info if exists
            if task.category:
                task_data['category_name'] = task.category.name
            else:
                task_data['category_name'] = None

            result.append(task_data)

        return result

    @staticmethod
    def get_task_by_id(task_id):
        """Get task by ID"""
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        return task

    @staticmethod
    def create_task(data):
        """
        Create new task

        Args:
            data: dict with task fields

        Returns:
            Created Task object

        Raises:
            ValueError: If validation fails
        """
        # Validate user exists
        if data.get('user_id'):
            user = User.query.get(data['user_id'])
            if not user:
                raise ValueError(f"User {data['user_id']} not found")

        # Validate category exists
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if not category:
                raise ValueError(f"Category {data['category_id']} not found")

        # Handle tags (convert list to string)
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = ','.join(data['tags'])

        task = Task(**data)

        try:
            db.session.add(task)
            db.session.commit()
            logger.info(f"Task created: {task.id} - {task.title}")
            return task

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise

    @staticmethod
    def update_task(task_id, data):
        """Update task"""
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Validate user if being updated
        if 'user_id' in data and data['user_id']:
            user = User.query.get(data['user_id'])
            if not user:
                raise ValueError(f"User {data['user_id']} not found")

        # Validate category if being updated
        if 'category_id' in data and data['category_id']:
            category = Category.query.get(data['category_id'])
            if not category:
                raise ValueError(f"Category {data['category_id']} not found")

        # Handle tags
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = ','.join(data['tags'])

        # Update fields
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            logger.info(f"Task updated: {task.id}")
            return task

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating task: {e}", exc_info=True)
            raise

    @staticmethod
    def delete_task(task_id):
        """Delete task"""
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        try:
            db.session.delete(task)
            db.session.commit()
            logger.info(f"Task deleted: {task_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting task: {e}", exc_info=True)
            raise

    @staticmethod
    def search_tasks(query=None, status=None, priority=None, user_id=None):
        """Search tasks with filters"""
        tasks_query = Task.query

        if query:
            # Sanitize LIKE query
            sanitized_query = query.replace('%', '\\%').replace('_', '\\_')
            tasks_query = tasks_query.filter(
                db.or_(
                    Task.title.like(f'%{sanitized_query}%'),
                    Task.description.like(f'%{sanitized_query}%')
                )
            )

        if status:
            tasks_query = tasks_query.filter(Task.status == status)

        if priority:
            tasks_query = tasks_query.filter(Task.priority == int(priority))

        if user_id:
            tasks_query = tasks_query.filter(Task.user_id == int(user_id))

        return tasks_query.all()

    @staticmethod
    def get_task_stats():
        """Get task statistics"""
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        # Count overdue tasks
        all_tasks = Task.query.all()
        overdue_count = sum(1 for task in all_tasks if task.is_overdue)

        stats = {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }

        return stats
