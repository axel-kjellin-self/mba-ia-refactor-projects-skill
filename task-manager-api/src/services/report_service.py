from src.models.task import Task
from src.models.user import User
from src.models.category import Category
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Report generation business logic"""

    @staticmethod
    def get_summary_report():
        """Generate summary report with all statistics"""
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        # Tasks by status
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        # Tasks by priority
        p1 = Task.query.filter_by(priority=1).count()
        p2 = Task.query.filter_by(priority=2).count()
        p3 = Task.query.filter_by(priority=3).count()
        p4 = Task.query.filter_by(priority=4).count()
        p5 = Task.query.filter_by(priority=5).count()

        # Overdue tasks - using centralized logic
        all_tasks = Task.query.all()
        overdue_list = []
        for task in all_tasks:
            if task.is_overdue:
                overdue_list.append({
                    'id': task.id,
                    'title': task.title,
                    'due_date': task.due_date.isoformat(),
                    'days_overdue': (datetime.utcnow() - task.due_date).days
                })

        # Recent activity
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done',
            Task.updated_at >= seven_days_ago
        ).count()

        # User productivity
        users = User.query.all()
        user_stats = []
        for user in users:
            user_tasks = Task.query.filter_by(user_id=user.id).all()
            total = len(user_tasks)
            completed = sum(1 for t in user_tasks if t.status == 'done')

            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
            })

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': pending,
                'in_progress': in_progress,
                'done': done,
                'cancelled': cancelled,
            },
            'tasks_by_priority': {
                'critical': p1,
                'high': p2,
                'medium': p3,
                'low': p4,
                'minimal': p5,
            },
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

        return report

    @staticmethod
    def get_user_report(user_id):
        """Generate report for specific user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        tasks = Task.query.filter_by(user_id=user_id).all()

        total = len(tasks)
        done = sum(1 for t in tasks if t.status == 'done')
        pending = sum(1 for t in tasks if t.status == 'pending')
        in_progress = sum(1 for t in tasks if t.status == 'in_progress')
        cancelled = sum(1 for t in tasks if t.status == 'cancelled')
        overdue = sum(1 for t in tasks if t.is_overdue)
        high_priority = sum(1 for t in tasks if t.priority <= 2)

        report = {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
            }
        }

        return report


class CategoryService:
    """Category business logic"""

    @staticmethod
    def get_all_categories():
        """Get all categories with task count"""
        categories = Category.query.all()
        result = []
        for category in categories:
            cat_data = category.to_dict()
            cat_data['task_count'] = Task.query.filter_by(category_id=category.id).count()
            result.append(cat_data)
        return result

    @staticmethod
    def create_category(data):
        """Create new category"""
        from src.config.database import db

        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#000000')
        )

        try:
            db.session.add(category)
            db.session.commit()
            logger.info(f"Category created: {category.id} - {category.name}")
            return category

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating category: {e}", exc_info=True)
            raise

    @staticmethod
    def update_category(cat_id, data):
        """Update category"""
        from src.config.database import db

        category = Category.query.get(cat_id)
        if not category:
            raise ValueError(f"Category {cat_id} not found")

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']

        try:
            db.session.commit()
            return category

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating category: {e}", exc_info=True)
            raise

    @staticmethod
    def delete_category(cat_id):
        """Delete category"""
        from src.config.database import db

        category = Category.query.get(cat_id)
        if not category:
            raise ValueError(f"Category {cat_id} not found")

        try:
            db.session.delete(category)
            db.session.commit()
            logger.info(f"Category deleted: {cat_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting category: {e}", exc_info=True)
            raise
