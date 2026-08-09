from flask import request, g
import logging
import time

logger = logging.getLogger(__name__)


def setup_logging(app):
    """Configure structured logging for the application"""

    # Configure logging format
    logging.basicConfig(
        level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    @app.before_request
    def before_request():
        """Log request start and set request start time"""
        g.start_time = time.time()

        logger.info(
            f"REQUEST: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )

    @app.after_request
    def after_request(response):
        """Log request completion with duration"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time

            logger.info(
                f"RESPONSE: {request.method} {request.path} "
                f"{response.status_code} {duration:.3f}s"
            )

        return response

    logger.info("Logging configured successfully")
