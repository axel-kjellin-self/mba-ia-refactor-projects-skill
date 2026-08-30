"""Application factory — composition root da aplicação.

Substitui o `app.py` que criava a app no import, com config hardcoded e
`db.create_all()` executando como efeito colateral de importação.
"""
from flask import Flask
from flask_cors import CORS

from src.config.database import init_db
from src.config.settings import Config, get_config
from src.middlewares.error_handler import register_error_handlers
from src.middlewares.logging_config import configure_logging
from src.routes import register_routes


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    config: type[Config] = get_config(config_name)
    config.validate()  # falha rápido se SECRET_KEY estiver ausente
    app.config.from_object(config)

    configure_logging(app)

    # CORS restrito a origens declaradas, não '*'.
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    init_db(app)
    register_error_handlers(app)
    register_routes(app)

    return app
