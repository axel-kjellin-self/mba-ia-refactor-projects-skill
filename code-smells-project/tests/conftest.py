"""Fixtures compartilhadas dos testes."""

import os
import tempfile

import pytest

# Configuração precisa existir antes de qualquer import de src.config.settings.
os.environ.setdefault("SECRET_KEY", "chave-de-teste-com-mais-de-32-caracteres-ok")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("SEED_ADMIN_PASSWORD", "senha-admin-de-teste")
os.environ.setdefault("LOG_LEVEL", "WARNING")


@pytest.fixture()
def app():
    """Aplicação com um banco SQLite temporário e isolado por teste."""
    from src.config.settings import Config

    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    original = Config.DATABASE_PATH
    Config.DATABASE_PATH = caminho

    from src.app_factory import create_app

    aplicacao = create_app()
    aplicacao.config.update(TESTING=True)

    yield aplicacao

    Config.DATABASE_PATH = original
    os.unlink(caminho)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def token_admin(client):
    """Token do admin criado pelo seed."""
    resposta = client.post(
        "/login", json={"email": "admin@loja.com", "senha": "senha-admin-de-teste"}
    )
    assert resposta.status_code == 200, resposta.get_json()
    return resposta.get_json()["dados"]["token"]


@pytest.fixture()
def token_cliente(client):
    """Cadastra um cliente e devolve seu token e id."""
    client.post(
        "/usuarios",
        json={
            "nome": "Cliente Teste",
            "email": "cliente@teste.com",
            "senha": "senha-forte-de-teste",
        },
    )
    resposta = client.post(
        "/login", json={"email": "cliente@teste.com", "senha": "senha-forte-de-teste"}
    )
    dados = resposta.get_json()["dados"]
    return dados["token"], dados["usuario"]["id"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
