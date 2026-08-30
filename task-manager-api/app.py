"""Entry point da aplicação."""
from src.app_factory import create_app
from src.config.settings import Config

app = create_app()

if __name__ == '__main__':
    # Host, porta e debug vêm do ambiente — antes eram `0.0.0.0` e `debug=True`
    # hardcoded, expondo o console interativo do Werkzeug.
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
