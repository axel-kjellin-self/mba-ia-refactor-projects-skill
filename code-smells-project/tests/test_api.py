"""Testes de integração cobrindo todos os endpoints e as correções de segurança."""

import os
import tempfile

import pytest

from src.app_factory import create_app, init_database
from src.config.settings import Settings
from src.services.relatorio_service import calcular_desconto

ADMIN_EMAIL = "admin@teste.local"
ADMIN_SENHA = "AdminSeguro#2026"
CLIENTE_SENHA = "ClienteSeguro#2026"


@pytest.fixture()
def app():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    settings = Settings(
        secret_key="chave-de-teste-nao-usada-em-producao",
        env="testing",
        debug=False,
        host="127.0.0.1",
        port=5000,
        database_path=caminho,
        jwt_expiration_minutes=15,
        cors_origins=["*"],
        seed_admin_email=ADMIN_EMAIL,
        seed_admin_password=ADMIN_SENHA,
    )
    aplicacao = create_app(settings)
    init_database(aplicacao)
    yield aplicacao
    os.unlink(caminho)


@pytest.fixture()
def client(app):
    return app.test_client()


def _token(client, email, senha):
    resposta = client.post("/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.get_json()
    return resposta.get_json()["dados"]["token"]


@pytest.fixture()
def admin_headers(client):
    return {"Authorization": f"Bearer {_token(client, ADMIN_EMAIL, ADMIN_SENHA)}"}


@pytest.fixture()
def cliente_headers(client):
    client.post(
        "/usuarios",
        json={"nome": "Cliente Teste", "email": "cliente@teste.local", "senha": CLIENTE_SENHA},
    )
    return {"Authorization": f"Bearer {_token(client, 'cliente@teste.local', CLIENTE_SENHA)}"}


# --- rotas públicas -------------------------------------------------------

def test_index_e_health(client):
    assert client.get("/").status_code == 200
    resposta = client.get("/health")
    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["status"] == "ok"
    assert corpo["counts"]["produtos"] == 10


def test_health_nao_expoe_secrets(client):
    corpo = client.get("/health").get_json()
    texto = str(corpo).lower()
    assert "secret" not in texto and "debug" not in texto and "db_path" not in texto


def test_listar_e_buscar_produto(client):
    corpo = client.get("/produtos").get_json()["dados"]
    assert corpo["total"] == 10 and len(corpo["itens"]) == 10
    assert client.get("/produtos/1").get_json()["dados"]["nome"] == "Notebook Gamer"
    assert client.get("/produtos/9999").status_code == 404


def test_busca_com_filtros(client):
    corpo = client.get("/produtos/busca?q=mouse").get_json()["dados"]
    assert corpo["total"] == 1
    corpo = client.get("/produtos/busca?categoria=moveis&preco_min=100").get_json()["dados"]
    assert corpo["total"] == 1


def test_busca_com_preco_invalido_retorna_400(client):
    """No legado, float('abc') estourava e virava 500."""
    assert client.get("/produtos/busca?preco_min=abc").status_code == 400


# --- segurança ------------------------------------------------------------

def test_endpoints_administrativos_removidos(client):
    assert client.post("/admin/query", json={"sql": "SELECT 1"}).status_code == 404
    assert client.post("/admin/reset-db").status_code == 404


def test_escrita_exige_autenticacao(client):
    assert client.post("/produtos", json={"nome": "X", "preco": 1, "estoque": 1}).status_code == 401
    assert client.get("/usuarios").status_code == 401
    assert client.get("/relatorios/vendas").status_code == 401
    assert client.post("/pedidos", json={"itens": []}).status_code == 401


def test_cliente_nao_acessa_rota_de_admin(client, cliente_headers):
    assert client.get("/usuarios", headers=cliente_headers).status_code == 403
    assert client.get("/relatorios/vendas", headers=cliente_headers).status_code == 403


def test_token_invalido_rejeitado(client):
    assert client.get("/me", headers={"Authorization": "Bearer nao-e-um-token"}).status_code == 401


def test_sql_injection_no_login_nao_funciona(client):
    """Payload que dava bypass no legado (WHERE email = 'admin' --')."""
    resposta = client.post("/login", json={"email": "admin@teste.local' --", "senha": "x"})
    assert resposta.status_code == 401


def test_sql_injection_na_busca_nao_vaza_dados(client):
    corpo = client.get("/produtos/busca?q=' OR '1'='1").get_json()["dados"]
    assert corpo["total"] == 0


def test_listagem_de_usuarios_nao_expoe_senha(client, admin_headers):
    itens = client.get("/usuarios", headers=admin_headers).get_json()["dados"]["itens"]
    assert itens and all("senha" not in u and "senha_hash" not in u for u in itens)


def test_senha_e_armazenada_com_hash(client, app):
    client.post(
        "/usuarios",
        json={"nome": "Hash Teste", "email": "hash@teste.local", "senha": CLIENTE_SENHA},
    )
    with app.app_context():
        from src.repositories import usuario_repository

        usuario = usuario_repository.buscar_por_email("hash@teste.local")
    assert usuario.senha_hash.startswith("$2b$")
    assert CLIENTE_SENHA not in usuario.senha_hash


def test_cliente_nao_le_pedidos_de_outro_usuario(client, cliente_headers):
    """IDOR presente no legado em /pedidos/usuario/<id>."""
    assert client.get("/pedidos/usuario/1", headers=cliente_headers).status_code == 403


# --- validação ------------------------------------------------------------

def test_senha_fraca_rejeitada(client):
    resposta = client.post(
        "/usuarios", json={"nome": "Fraco", "email": "fraco@teste.local", "senha": "123456"}
    )
    assert resposta.status_code == 400


def test_email_duplicado_retorna_409(client):
    payload = {"nome": "Dup", "email": "dup@teste.local", "senha": CLIENTE_SENHA}
    assert client.post("/usuarios", json=payload).status_code == 201
    assert client.post("/usuarios", json=payload).status_code == 409


def test_produto_com_tipo_invalido_retorna_400(client, admin_headers):
    """No legado, preco='abc' causava TypeError → 500."""
    resposta = client.post(
        "/produtos",
        json={"nome": "Teste", "preco": "abc", "estoque": 1},
        headers=admin_headers,
    )
    assert resposta.status_code == 400


def test_categoria_invalida_rejeitada_no_update(client, admin_headers):
    """A validação de categoria existia no create mas faltava no update legado."""
    resposta = client.put(
        "/produtos/1",
        json={"nome": "Teste", "preco": 10, "estoque": 1, "categoria": "inexistente"},
        headers=admin_headers,
    )
    assert resposta.status_code == 400


# --- CRUD de produto ------------------------------------------------------

def test_ciclo_completo_de_produto(client, admin_headers):
    criado = client.post(
        "/produtos",
        json={"nome": "Produto Novo", "preco": 10.5, "estoque": 3, "categoria": "livros"},
        headers=admin_headers,
    )
    assert criado.status_code == 201
    produto_id = criado.get_json()["dados"]["id"]

    atualizado = client.put(
        f"/produtos/{produto_id}",
        json={"nome": "Produto Editado", "preco": 20, "estoque": 5, "categoria": "livros"},
        headers=admin_headers,
    )
    assert atualizado.status_code == 200
    assert client.get(f"/produtos/{produto_id}").get_json()["dados"]["nome"] == "Produto Editado"

    assert client.delete(f"/produtos/{produto_id}", headers=admin_headers).status_code == 200
    assert client.get(f"/produtos/{produto_id}").status_code == 404


# --- pedidos --------------------------------------------------------------

def test_criar_pedido_debita_estoque(client, cliente_headers):
    estoque_inicial = client.get("/produtos/2").get_json()["dados"]["estoque"]
    resposta = client.post(
        "/pedidos", json={"itens": [{"produto_id": 2, "quantidade": 3}]}, headers=cliente_headers
    )
    assert resposta.status_code == 201
    assert resposta.get_json()["dados"]["total"] == pytest.approx(89.90 * 3, abs=0.01)
    assert client.get("/produtos/2").get_json()["dados"]["estoque"] == estoque_inicial - 3


def test_pedido_com_estoque_insuficiente_nao_persiste_nada(client, cliente_headers, admin_headers):
    resposta = client.post(
        "/pedidos", json={"itens": [{"produto_id": 6, "quantidade": 999}]}, headers=cliente_headers
    )
    assert resposta.status_code == 422
    assert client.get("/produtos/6").get_json()["dados"]["estoque"] == 8
    assert client.get("/pedidos", headers=admin_headers).get_json()["dados"]["total"] == 0


def test_pedido_com_produto_inexistente_retorna_404(client, cliente_headers):
    resposta = client.post(
        "/pedidos", json={"itens": [{"produto_id": 9999, "quantidade": 1}]}, headers=cliente_headers
    )
    assert resposta.status_code == 404


def test_pedido_sem_itens_retorna_400(client, cliente_headers):
    assert client.post("/pedidos", json={"itens": []}, headers=cliente_headers).status_code == 400


def test_listagem_de_pedidos_traz_itens_com_nome(client, cliente_headers, admin_headers):
    client.post(
        "/pedidos", json={"itens": [{"produto_id": 1, "quantidade": 1}]}, headers=cliente_headers
    )
    pedidos = client.get("/pedidos", headers=admin_headers).get_json()["dados"]["itens"]
    assert len(pedidos) == 1
    assert pedidos[0]["itens"][0]["produto_nome"] == "Notebook Gamer"

    meus = client.get("/pedidos/usuario/2", headers=cliente_headers)
    assert meus.status_code == 200 and meus.get_json()["dados"]["total"] == 1


def test_cancelamento_devolve_estoque(client, cliente_headers, admin_headers):
    """O legado apenas logava 'Devolver estoque' e nunca devolvia."""
    estoque_inicial = client.get("/produtos/3").get_json()["dados"]["estoque"]
    pedido = client.post(
        "/pedidos", json={"itens": [{"produto_id": 3, "quantidade": 2}]}, headers=cliente_headers
    ).get_json()["dados"]
    assert client.get("/produtos/3").get_json()["dados"]["estoque"] == estoque_inicial - 2

    resposta = client.put(
        f"/pedidos/{pedido['pedido_id']}/status",
        json={"status": "cancelado"},
        headers=admin_headers,
    )
    assert resposta.status_code == 200
    assert client.get("/produtos/3").get_json()["dados"]["estoque"] == estoque_inicial


def test_status_invalido_retorna_400(client, cliente_headers, admin_headers):
    pedido = client.post(
        "/pedidos", json={"itens": [{"produto_id": 1, "quantidade": 1}]}, headers=cliente_headers
    ).get_json()["dados"]
    resposta = client.put(
        f"/pedidos/{pedido['pedido_id']}/status", json={"status": "voando"}, headers=admin_headers
    )
    assert resposta.status_code == 400


# --- relatórios -----------------------------------------------------------

def test_relatorio_de_vendas(client, cliente_headers, admin_headers):
    client.post(
        "/pedidos", json={"itens": [{"produto_id": 1, "quantidade": 1}]}, headers=cliente_headers
    )
    dados = client.get("/relatorios/vendas", headers=admin_headers).get_json()["dados"]
    assert dados["total_pedidos"] == 1
    assert dados["faturamento_bruto"] == pytest.approx(5999.99, abs=0.01)
    # 5999.99 cai na faixa de 5% (> 5.000 e <= 10.000)
    assert dados["desconto_aplicavel"] == pytest.approx(300.0, abs=0.01)
    assert dados["faturamento_liquido"] == pytest.approx(5699.99, abs=0.01)
    assert dados["pedidos_por_status"]["pendente"] == 1


@pytest.mark.parametrize(
    "faturamento,esperado",
    [(0, 0), (1000, 0), (1000.01, 20.0002), (5000, 100), (5000.01, 250.0005), (20000, 2000)],
)
def test_faixas_de_desconto(faturamento, esperado):
    """Regra de negócio testável sem banco nem HTTP."""
    assert calcular_desconto(faturamento) == pytest.approx(esperado)
