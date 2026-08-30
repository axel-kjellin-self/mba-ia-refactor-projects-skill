"""Instância única do SQLAlchemy e inicialização do banco."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """Vincula o SQLAlchemy à app e garante a criação do schema."""
    db.init_app(app)

    # Importa os models para que fiquem registrados no metadata antes do
    # create_all(). O import é local para evitar ciclo com config.database.
    from src.models import Category, Task, User  # noqa: F401

    with app.app_context():
        db.create_all()
