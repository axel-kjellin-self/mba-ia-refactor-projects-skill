"""Envio de notificações por e-mail.

Credenciais agora vêm de `Config` (antes eram literais no código) e o cliente
SMTP é injetável, tornando o service testável com mock.
"""
import logging
import smtplib
from email.message import EmailMessage
from typing import Callable

from src.config.settings import Config

logger = logging.getLogger(__name__)


def _default_smtp_client() -> smtplib.SMTP:
    client = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10)
    client.starttls()
    if Config.SMTP_USER and Config.SMTP_PASSWORD:
        client.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
    return client


class NotificationService:
    def __init__(self, smtp_factory: Callable[[], smtplib.SMTP] | None = None) -> None:
        self.smtp_factory = smtp_factory or _default_smtp_client

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Envia um e-mail. No-op quando SMTP_ENABLED=false (default)."""
        if not Config.SMTP_ENABLED:
            logger.info('SMTP desabilitado; e-mail para %s não enviado', to)
            return False

        message = EmailMessage()
        message['From'] = Config.SMTP_USER
        message['To'] = to
        message['Subject'] = subject
        message.set_content(body)

        try:
            with self.smtp_factory() as client:
                client.send_message(message)
        except (smtplib.SMTPException, OSError):
            logger.error('Falha ao enviar e-mail para %s', to, exc_info=True)
            return False

        logger.info('E-mail enviado para %s', to)
        return True

    def notify_task_assigned(self, user, task) -> bool:
        return self.send_email(
            user.email,
            f'Nova task atribuída: {task.title}',
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}',
        )

    def notify_task_overdue(self, user, task) -> bool:
        return self.send_email(
            user.email,
            f'Task atrasada: {task.title}',
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f'Data limite: {task.due_date}',
        )
