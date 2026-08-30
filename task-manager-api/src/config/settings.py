"""Configuração da aplicação carregada a partir de variáveis de ambiente.

Substitui os valores hardcoded que antes viviam em `app.py` e
`services/notification_service.py` (findings CRITICAL: Hardcoded Secrets).
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    """Configuração base — nunca contém valores sensíveis literais."""

    SECRET_KEY: str | None = os.getenv('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # JWT
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRES_SECONDS: int = int(os.getenv('JWT_EXPIRES_SECONDS', '3600'))

    # CORS — lista separada por vírgula. Nunca '*' por padrão.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
        if origin.strip()
    ]

    # SMTP (notificações)
    SMTP_HOST: str = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER: str | None = os.getenv('SMTP_USER')
    SMTP_PASSWORD: str | None = os.getenv('SMTP_PASSWORD')
    SMTP_ENABLED: bool = _as_bool(os.getenv('SMTP_ENABLED'), False)

    # Servidor
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', '5000'))
    DEBUG: bool = _as_bool(os.getenv('FLASK_DEBUG'), False)

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls) -> None:
        """Falha rápido no boot se um secret obrigatório estiver ausente."""
        missing = [name for name in ('SECRET_KEY',) if not getattr(cls, name)]
        if missing:
            raise RuntimeError(
                f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing)}. "
                'Copie .env.example para .env e preencha os valores.'
            )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = Config.SECRET_KEY or 'testing-only-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    env = name or os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
