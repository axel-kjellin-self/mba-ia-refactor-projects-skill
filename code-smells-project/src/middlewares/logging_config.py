"""Configuração de logging e log de acesso.

Substitui as 14 chamadas a ``print()`` espalhadas pelo código original.
"""

import logging
import time

from flask import Flask, g, request

from src.config.settings import Config

_FORMATO = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"


def configurar_logging() -> None:
    """Configura o logger raiz uma única vez."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
        format=_FORMATO,
    )


def register_request_logging(app: Flask) -> None:
    """Registra um log por request, com método, rota, status e duração."""
    logger = logging.getLogger("access")

    @app.before_request
    def _inicio():
        g.inicio_request = time.perf_counter()

    @app.after_request
    def _fim(response):
        inicio = g.pop("inicio_request", None)
        duracao_ms = (time.perf_counter() - inicio) * 1000 if inicio else 0.0

        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.path,
            response.status_code,
            duracao_ms,
        )
        return response
