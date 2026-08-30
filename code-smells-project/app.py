"""Entry point da aplicação.

Para desenvolvimento local: ``python app.py``.
Em produção, use um servidor WSGI apontando para ``app``:
``gunicorn "app:app"``.
"""

from src.app_factory import create_app
from src.config.settings import Config

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
