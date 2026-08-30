"""Logging estruturado, substituindo os `print()` usados como log."""
import logging
import time

from flask import Flask, g, request

logger = logging.getLogger('task_manager.access')


def configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO'), logging.INFO),
        format='%(asctime)s %(levelname)-8s %(name)s: %(message)s',
    )

    @app.before_request
    def _start_timer() -> None:
        g.request_started_at = time.perf_counter()

    @app.after_request
    def _log_request(response):
        started = getattr(g, 'request_started_at', None)
        duration_ms = (time.perf_counter() - started) * 1000 if started else 0
        logger.info(
            '%s %s -> %s (%.1fms)',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
