"""Configuração da aplicação carregada a partir do ambiente.

Substitui os valores hardcoded que antes viviam em ``app.py`` (SECRET_KEY,
DEBUG) e em ``database.py`` (caminho do banco).
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


class Config:
    """Configuração base. Valores sensíveis vêm exclusivamente do ambiente."""

    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = _env_bool("DEBUG", False)

    SECRET_KEY: str | None = os.getenv("SECRET_KEY")

    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "loja.db")

    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_SECONDS: int = _env_int("JWT_EXPIRES_SECONDS", 3600)

    # Origens permitidas para CORS. Antes era liberado para qualquer origem.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = _env_int("PORT", 5000)

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Habilita o seed de dados de exemplo apenas fora de produção.
    SEED_DATA: bool = _env_bool("SEED_DATA", True)
    SEED_ADMIN_PASSWORD: str | None = os.getenv("SEED_ADMIN_PASSWORD")

    @classmethod
    def validate(cls) -> None:
        """Falha o boot se configuração obrigatória estiver ausente.

        É preferível não subir a subir com uma chave default previsível.
        """
        missing = [name for name in ("SECRET_KEY",) if not getattr(cls, name)]
        if missing:
            raise RuntimeError(
                "Configuração obrigatória ausente: "
                + ", ".join(missing)
                + ". Copie .env.example para .env e preencha os valores."
            )

        if len(cls.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY deve ter no mínimo 32 caracteres.")

        if cls.ENV == "production":
            if cls.DEBUG:
                raise RuntimeError("DEBUG não pode estar habilitado em produção.")
            if "*" in cls.CORS_ORIGINS:
                raise RuntimeError("CORS_ORIGINS não pode ser '*' em produção.")
