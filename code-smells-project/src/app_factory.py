"""Application factory.

Composition root: monta configuração, banco, middlewares e rotas. Não contém
nenhuma regra de negócio nem acesso direto ao banco — o ``app.py`` original
implementava handlers com SQL inline.
"""

import logging

from flask import Flask
from flask_cors import CORS

from src.config import database
from src.config.database import conexao_avulsa
from src.config.schema import init_db
from src.config.settings import Config
from src.middlewares.error_handler import register_error_handlers
from src.middlewares.logging_config import configurar_logging, register_request_logging
from src.routes import register_routes

logger = logging.getLogger(__name__)


def create_app(config: type[Config] = Config, *, inicializar_banco: bool = True) -> Flask:
    """Cria e configura a aplicação Flask."""
    configurar_logging()
    config.validate()

    app = Flask(__name__)
    app.config.from_object(config)

    # CORS restrito às origens configuradas, com credenciais habilitadas apenas
    # para elas. Antes, qualquer origem podia chamar qualquer rota.
    CORS(
        app,
        origins=config.CORS_ORIGINS,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    database.init_app(app)

    if inicializar_banco:
        with conexao_avulsa() as conexao:
            init_db(conexao)

    register_request_logging(app)
    register_error_handlers(app)
    register_routes(app)

    logger.info(
        "Aplicação inicializada (env=%s, debug=%s, db=%s)",
        config.ENV,
        config.DEBUG,
        config.DATABASE_PATH,
    )
    return app
