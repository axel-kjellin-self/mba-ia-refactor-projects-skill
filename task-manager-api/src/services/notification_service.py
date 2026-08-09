import smtplib
from datetime import datetime
from src.config.settings import Config
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Email notification service"""

    def __init__(self):
        self.notifications = []
        self.email_host = Config.SMTP_SERVER
        self.email_port = Config.SMTP_PORT
        self.email_user = Config.SMTP_USER
        self.email_password = Config.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        """
        Send email notification

        NOTE: This is a placeholder implementation.
        In production, use a proper email service like SendGrid, Mailgun, etc.
        """
        try:
            if not self.email_user or not self.email_password:
                logger.warning("SMTP credentials not configured. Email not sent.")
                return False

            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()

            logger.info(f"Email sent to {to}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False

    def notify_task_assigned(self, user, task):
        """Notify user of task assignment"""
        subject = f"New task assigned: {task.title}"
        body = f"Hello {user.name},\n\nThe task '{task.title}' has been assigned to you.\n\nPriority: {task.priority}\nStatus: {task.status}"

        self.send_email(user.email, subject, body)

        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.utcnow()
        })

    def notify_task_overdue(self, user, task):
        """Notify user of overdue task"""
        subject = f"Task overdue: {task.title}"
        body = f"Hello {user.name},\n\nThe task '{task.title}' is overdue!\n\nDue date: {task.due_date}"

        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        """Get notifications for specific user"""
        return [n for n in self.notifications if n['user_id'] == user_id]
