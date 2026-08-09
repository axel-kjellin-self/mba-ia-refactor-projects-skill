from flask import request
import logging
import time

logger = logging.getLogger(__name__)


def setup_logging(app):
    """Configure structured logging for the application"""

    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Log request/response
    @app.before_request
    def log_request():
        """Log incoming request"""
        request.start_time = time.time()
        logger.info(f"{request.method} {request.path} - Request started")

    @app.after_request
    def log_response(response):
        """Log response with duration"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        return response

    logger.info("Logging middleware configured")
