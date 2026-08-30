"""Composition root: monta a aplicação a partir das camadas.

Toda a fiação (config → banco → middlewares → rotas) acontece aqui, o que
permite instanciar a app em testes com um banco temporário.
"""

import logging

import click
from flask import Flask
from flask_cors import CORS

from src.config.database import init_app as init_db_lifecycle
from src.config.schema import criar_schema, init_database, popular_dados_iniciais
from src.config.settings import Settings, load_settings
from src.middlewares.error_handler import register_error_handlers
from src.middlewares.logging_config import configurar_logging
from src.routes import register_blueprints

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or load_settings()
    configurar_logging(settings.log_level)

    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DATABASE_PATH"] = settings.database_path
    app.config["DEBUG"] = settings.debug
    # Evita que o Flask converta exceções em 500 antes dos nossos handlers.
    app.config["JSON_SORT_KEYS"] = False

    CORS(app, origins=settings.cors_origins)

    init_db_lifecycle(app)
    register_error_handlers(app)
    register_blueprints(app)
    _registrar_comandos(app)

    logger.info("Aplicação inicializada (env=%s, debug=%s)", settings.env, settings.debug)
    return app


def _registrar_comandos(app: Flask) -> None:
    @app.cli.command("init-db")
    @click.option("--seed", is_flag=True, help="Insere catálogo e admin de exemplo.")
    def init_db_command(seed: bool):
        """Cria o schema do banco (e opcionalmente os dados iniciais)."""
        criar_schema()
        if seed:
            popular_dados_iniciais(app.config["SETTINGS"])
        click.echo("Banco inicializado.")


__all__ = ["create_app", "init_database"]
