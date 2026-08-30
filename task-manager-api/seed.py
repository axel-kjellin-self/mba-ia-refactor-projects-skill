"""Popula o banco com dados iniciais para desenvolvimento.

As senhas vêm de SEED_PASSWORD no .env — antes eram literais triviais
('1234', 'abcd', 'pass'), incluindo a da conta admin.
"""
import os
import sys
from datetime import datetime, timedelta

from src.app_factory import create_app
from src.config.constants import TaskStatus, UserRole
from src.config.database import db
from src.models import Category, Task, User
from src.schemas.user_schema import validate_password_strength

USERS = [
    ('João Silva', 'joao@email.com', UserRole.ADMIN.value),
    ('Maria Santos', 'maria@email.com', UserRole.USER.value),
    ('Pedro Oliveira', 'pedro@email.com', UserRole.MANAGER.value),
]

CATEGORIES = [
    ('Backend', 'Tarefas de backend', '#3498db'),
    ('Frontend', 'Tarefas de frontend', '#2ecc71'),
    ('DevOps', 'Tarefas de infraestrutura', '#e74c3c'),
    ('Bug', 'Correção de bugs', '#e67e22'),
]

TASKS = [
    ('Implementar autenticação JWT', 'Adicionar autenticação real com JWT',
     TaskStatus.PENDING, 1, 0, 0, -3, None),
    ('Criar tela de login', 'Tela de login responsiva',
     TaskStatus.IN_PROGRESS, 2, 1, 1, 5, None),
    ('Configurar CI/CD', 'Pipeline com GitHub Actions',
     TaskStatus.DONE, 2, 2, 2, None, 'devops,ci,github'),
    ('Corrigir bug no filtro de busca', 'Filtro não funciona com caracteres especiais',
     TaskStatus.PENDING, 1, 0, 3, -1, None),
    ('Adicionar paginação na API', 'Endpoints retornam todos os registros',
     TaskStatus.PENDING, 3, 0, 0, 10, None),
    ('Escrever testes unitários', 'Cobertura mínima de 80%',
     TaskStatus.PENDING, 2, 1, 0, None, None),
    ('Documentar API com Swagger', 'Gerar documentação automática',
     TaskStatus.CANCELLED, 4, 2, 0, None, None),
    ('Refatorar models', 'Melhorar organização dos models',
     TaskStatus.IN_PROGRESS, 3, 1, 0, None, 'refactor,tech-debt'),
    ('Configurar monitoramento', 'Prometheus + Grafana',
     TaskStatus.PENDING, 4, 2, 2, 20, None),
    ('Melhorar validações de input', 'Usar marshmallow ou pydantic',
     TaskStatus.PENDING, 3, 0, 0, None, 'improvement,validation'),
]


def seed_data() -> None:
    password = os.getenv('SEED_PASSWORD')
    if not password:
        sys.exit('Defina SEED_PASSWORD no .env antes de rodar o seed.')
    validate_password_strength(password)

    app = create_app()
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        users = []
        for name, email, role in USERS:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            users.append(user)

        categories = [
            Category(name=name, description=description, color=color)
            for name, description, color in CATEGORIES
        ]
        db.session.add_all(categories)
        db.session.commit()

        now = datetime.utcnow()
        for title, description, status, priority, u_idx, c_idx, due_offset, tags in TASKS:
            db.session.add(Task(
                title=title,
                description=description,
                status=status.value,
                priority=priority,
                user_id=users[u_idx].id,
                category_id=categories[c_idx].id,
                due_date=now + timedelta(days=due_offset) if due_offset is not None else None,
                tags=tags,
            ))
        db.session.commit()

        print('Seed concluído com sucesso!')
        print(f'  {User.query.count()} usuários')
        print(f'  {Category.query.count()} categorias')
        print(f'  {Task.query.count()} tasks')
        print(f'  Login: {USERS[0][1]} (admin) — senha em SEED_PASSWORD')


if __name__ == '__main__':
    seed_data()
