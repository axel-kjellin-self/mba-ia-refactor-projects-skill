"""Entry point da aplicação.

Em produção use um WSGI server apontando para ``app:app``:
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

from src.app_factory import create_app, init_database
from src.config.settings import load_settings

settings = load_settings()
app = create_app(settings)

# Em desenvolvimento o schema é criado no boot para manter o `python app.py`
# funcionando sem passos extras. Em produção use `flask init-db` explicitamente.
if not settings.is_production:
    init_database(app)

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
