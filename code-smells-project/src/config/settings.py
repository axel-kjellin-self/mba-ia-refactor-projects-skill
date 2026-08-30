"""Configuração da aplicação, carregada exclusivamente de variáveis de ambiente.

Nenhum secret é definido em código: a SECRET_KEY é obrigatória em produção e a
ausência dela interrompe o boot em vez de cair num valor default inseguro.
"""

import os
import secrets
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Configuração ausente ou inválida — impede o boot da aplicação."""


def _env_bool(name: str, default: bool = False) -> bool:
    valor = os.environ.get(name)
    if valor is None:
        return default
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    valor = os.environ.get(name)
    if valor is None or valor.strip() == "":
        return default
    try:
        return int(valor)
    except ValueError as exc:
        raise ConfigError(f"{name} deve ser um número inteiro, recebido: {valor!r}") from exc


@dataclass(frozen=True)
class Settings:
    secret_key: str
    env: str
    debug: bool
    host: str
    port: int
    database_path: str
    jwt_expiration_minutes: int
    cors_origins: list = field(default_factory=list)
    log_level: str = "INFO"
    seed_admin_email: str = ""
    seed_admin_password: str = ""

    @property
    def is_production(self) -> bool:
        return self.env == "production"


def load_settings() -> Settings:
    """Monta as Settings a partir do ambiente, validando o que é crítico."""
    env = os.environ.get("FLASK_ENV", "development").strip().lower()
    is_production = env == "production"

    secret_key = os.environ.get("SECRET_KEY", "").strip()
    if not secret_key:
        if is_production:
            raise ConfigError(
                "SECRET_KEY é obrigatória em produção. Defina a variável de ambiente "
                "(veja .env.example) antes de iniciar a aplicação."
            )
        # Em desenvolvimento geramos uma chave efêmera: os tokens deixam de valer a
        # cada restart, o que é preferível a um secret fixo versionado no código.
        secret_key = secrets.token_urlsafe(48)

    debug = _env_bool("DEBUG", default=False)
    if is_production and debug:
        raise ConfigError("DEBUG não pode estar habilitado em produção.")

    origens = os.environ.get("CORS_ORIGINS", "").strip()
    cors_origins = [o.strip() for o in origens.split(",") if o.strip()] or ["*"]

    return Settings(
        secret_key=secret_key,
        env=env,
        debug=debug,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=_env_int("PORT", 5000),
        database_path=os.environ.get("DATABASE_PATH", "loja.db"),
        jwt_expiration_minutes=_env_int("JWT_EXPIRATION_MINUTES", 60),
        cors_origins=cors_origins,
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        seed_admin_email=os.environ.get("SEED_ADMIN_EMAIL", "").strip(),
        seed_admin_password=os.environ.get("SEED_ADMIN_PASSWORD", "").strip(),
    )
