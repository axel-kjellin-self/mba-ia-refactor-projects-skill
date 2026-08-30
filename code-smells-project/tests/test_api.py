"""Testes de integração da API.

Cobrem tanto o comportamento funcional preservado quanto as vulnerabilidades
identificadas na auditoria, garantindo que não regridam.
"""

from tests.conftest import auth


class TestRotasPublicas:
    def test_index(self, client):
        resposta = client.get("/")
        assert resposta.status_code == 200
        assert resposta.get_json()["versao"] == "2.0.0"

    def test_health_nao_expoe_segredos(self, client):
        resposta = client.get("/health")
        corpo = resposta.get_json()

        assert resposta.status_code == 200
        assert corpo["status"] == "ok"
        # O /health original devolvia secret_key, debug e db_path.
        assert "secret_key" not in corpo
        assert "debug" not in corpo
        assert "db_path" not in corpo

    def test_listar_produtos_e_publico(self, client):
        resposta = client.get("/produtos")
        assert resposta.status_code == 200
        assert len(resposta.get_json()["dados"]) == 10

    def test_produto_inexistente_retorna_404(self, client):
        assert client.get("/produtos/9999").status_code == 404


class TestSegurancaEndpointsRemovidos:
    def test_reset_db_nao_existe(self, client):
        assert client.post("/admin/reset-db").status_code == 404

    def test_query_arbitraria_nao_existe(self, client):
        assert client.post("/admin/query", json={"sql": "SELECT 1"}).status_code == 404


class TestSqlInjection:
    def test_login_nao_permite_bypass(self, client):
        """O payload clássico de bypass deve falhar como credencial inválida."""
        resposta = client.post(
            "/login", json={"email": "admin@loja.com' --", "senha": "qualquer"}
        )
        assert resposta.status_code in (400, 401)

    def test_busca_com_payload_de_injecao_nao_quebra(self, client):
        resposta = client.get("/produtos/busca?q=' OR '1'='1")
        assert resposta.status_code == 200
        # Nenhum produto contém a string literal buscada.
        assert resposta.get_json()["dados"] == []

    def test_curingas_do_like_sao_literais(self, client):
        resposta = client.get("/produtos/busca?q=%")
        assert resposta.status_code == 200
        assert resposta.get_json()["dados"] == []


class TestAutenticacao:
    def test_login_retorna_token(self, client, token_admin):
        assert isinstance(token_admin, str) and token_admin.count(".") == 2

    def test_login_invalido_retorna_401(self, client):
        resposta = client.post(
            "/login", json={"email": "admin@loja.com", "senha": "senha-completamente-errada"}
        )
        assert resposta.status_code == 401

    def test_rota_protegida_sem_token_retorna_401(self, client):
        assert client.get("/usuarios").status_code == 401

    def test_token_invalido_retorna_401(self, client):
        resposta = client.get("/usuarios", headers=auth("token.falso.aqui"))
        assert resposta.status_code == 401

    def test_cliente_nao_acessa_rota_de_admin(self, client, token_cliente):
        token, _ = token_cliente
        assert client.get("/usuarios", headers=auth(token)).status_code == 403


class TestExposicaoDeSenhas:
    def test_listagem_de_usuarios_nao_expoe_senha(self, client, token_admin):
        resposta = client.get("/usuarios", headers=auth(token_admin))
        assert resposta.status_code == 200

        for usuario in resposta.get_json()["dados"]:
            assert "senha" not in usuario
            assert "senha_hash" not in usuario

    def test_login_nao_devolve_senha(self, client, token_cliente):
        token, usuario_id = token_cliente
        resposta = client.get(f"/usuarios/{usuario_id}", headers=auth(token))
        assert "senha" not in resposta.get_json()["dados"]

    def test_senha_e_armazenada_com_hash(self, app):
        """A senha nunca deve estar recuperável em texto plano no banco."""
        from src.config.database import conexao_avulsa

        with app.app_context(), conexao_avulsa() as conexao:
            row = conexao.execute(
                "SELECT senha_hash FROM usuarios WHERE email = ?", ("admin@loja.com",)
            ).fetchone()

        assert row is not None
        assert row["senha_hash"].startswith("$2b$")
        assert "senha-admin-de-teste" not in row["senha_hash"]


class TestAutorizacaoDeRecursos:
    def test_cliente_nao_le_pedidos_de_outro_usuario(self, client, token_cliente):
        token, usuario_id = token_cliente
        resposta = client.get(f"/pedidos/usuario/{usuario_id + 999}", headers=auth(token))
        assert resposta.status_code == 403

    def test_cliente_le_os_proprios_pedidos(self, client, token_cliente):
        token, usuario_id = token_cliente
        resposta = client.get(f"/pedidos/usuario/{usuario_id}", headers=auth(token))
        assert resposta.status_code == 200


class TestProdutos:
    def test_criar_produto_exige_admin(self, client, token_cliente):
        token, _ = token_cliente
        resposta = client.post(
            "/produtos",
            json={"nome": "Produto X", "preco": 10.0, "estoque": 5},
            headers=auth(token),
        )
        assert resposta.status_code == 403

    def test_admin_cria_produto(self, client, token_admin):
        resposta = client.post(
            "/produtos",
            json={
                "nome": "Produto Novo",
                "descricao": "Teste",
                "preco": 99.9,
                "estoque": 7,
                "categoria": "eletronicos",
            },
            headers=auth(token_admin),
        )
        assert resposta.status_code == 201
        assert resposta.get_json()["dados"]["nome"] == "Produto Novo"

    def test_preco_nao_numerico_retorna_400(self, client, token_admin):
        """No código original isso virava um TypeError capturado como 500."""
        resposta = client.post(
            "/produtos",
            json={"nome": "Produto", "preco": "abc", "estoque": 1},
            headers=auth(token_admin),
        )
        assert resposta.status_code == 400

    def test_preco_negativo_retorna_400(self, client, token_admin):
        resposta = client.post(
            "/produtos",
            json={"nome": "Produto", "preco": -1, "estoque": 1},
            headers=auth(token_admin),
        )
        assert resposta.status_code == 400

    def test_atualizacao_valida_categoria(self, client, token_admin):
        """O PUT original não validava categoria, ao contrário do POST."""
        resposta = client.put(
            "/produtos/1",
            json={
                "nome": "Produto",
                "preco": 10.0,
                "estoque": 1,
                "categoria": "categoria-inexistente",
            },
            headers=auth(token_admin),
        )
        assert resposta.status_code == 400

    def test_preco_min_invalido_retorna_400(self, client):
        resposta = client.get("/produtos/busca?preco_min=abc")
        assert resposta.status_code == 400


class TestPedidos:
    def test_criar_pedido_exige_autenticacao(self, client):
        resposta = client.post("/pedidos", json={"itens": [{"produto_id": 1, "quantidade": 1}]})
        assert resposta.status_code == 401

    def test_criar_pedido_calcula_total_e_baixa_estoque(self, client, token_cliente):
        token, _ = token_cliente
        estoque_antes = client.get("/produtos/2").get_json()["dados"]["estoque"]
        preco = client.get("/produtos/2").get_json()["dados"]["preco"]

        resposta = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 2, "quantidade": 3}]},
            headers=auth(token),
        )
        assert resposta.status_code == 201

        pedido = resposta.get_json()["dados"]
        assert pedido["total"] == round(preco * 3, 2)
        assert pedido["status"] == "pendente"
        assert len(pedido["itens"]) == 1

        estoque_depois = client.get("/produtos/2").get_json()["dados"]["estoque"]
        assert estoque_depois == estoque_antes - 3

    def test_quantidade_negativa_e_rejeitada(self, client, token_cliente):
        """No código original, quantidade negativa aumentava o estoque."""
        token, _ = token_cliente
        resposta = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 1, "quantidade": -5}]},
            headers=auth(token),
        )
        assert resposta.status_code == 400

    def test_estoque_insuficiente_retorna_422(self, client, token_cliente):
        """Quantidade válida, porém acima do estoque (produto 1 tem 10 unidades)."""
        token, _ = token_cliente
        resposta = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 1, "quantidade": 500}]},
            headers=auth(token),
        )
        assert resposta.status_code == 422

    def test_quantidade_acima_do_limite_retorna_400(self, client, token_cliente):
        """Acima de QUANTIDADE_MAX a requisição é barrada na validação."""
        token, _ = token_cliente
        resposta = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 1, "quantidade": 99999}]},
            headers=auth(token),
        )
        assert resposta.status_code == 400

    def test_produto_inexistente_retorna_404(self, client, token_cliente):
        token, _ = token_cliente
        resposta = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 99999, "quantidade": 1}]},
            headers=auth(token),
        )
        assert resposta.status_code == 404

    def test_pedido_nao_pode_ser_criado_para_outro_usuario(self, client, token_cliente):
        """O usuario_id vem do token; o campo no corpo é ignorado."""
        token, usuario_id = token_cliente
        resposta = client.post(
            "/pedidos",
            json={"usuario_id": 1, "itens": [{"produto_id": 3, "quantidade": 1}]},
            headers=auth(token),
        )
        assert resposta.status_code == 201
        assert resposta.get_json()["dados"]["usuario_id"] == usuario_id

    def test_cancelamento_repoe_estoque(self, client, token_admin, token_cliente):
        token, _ = token_cliente
        estoque_antes = client.get("/produtos/4").get_json()["dados"]["estoque"]

        criacao = client.post(
            "/pedidos",
            json={"itens": [{"produto_id": 4, "quantidade": 2}]},
            headers=auth(token),
        )
        pedido_id = criacao.get_json()["dados"]["id"]

        resposta = client.put(
            f"/pedidos/{pedido_id}/status",
            json={"status": "cancelado"},
            headers=auth(token_admin),
        )
        assert resposta.status_code == 200

        estoque_depois = client.get("/produtos/4").get_json()["dados"]["estoque"]
        assert estoque_depois == estoque_antes

    def test_status_invalido_retorna_400(self, client, token_admin):
        resposta = client.put(
            "/pedidos/1/status", json={"status": "inexistente"}, headers=auth(token_admin)
        )
        assert resposta.status_code == 400


class TestRelatorios:
    def test_relatorio_exige_admin(self, client, token_cliente):
        token, _ = token_cliente
        assert client.get("/relatorios/vendas", headers=auth(token)).status_code == 403

    def test_relatorio_de_vendas(self, client, token_admin):
        resposta = client.get("/relatorios/vendas", headers=auth(token_admin))
        assert resposta.status_code == 200

        dados = resposta.get_json()["dados"]
        assert dados["total_pedidos"] == 0
        assert dados["faturamento_bruto"] == 0
        assert dados["ticket_medio"] == 0


class TestRegrasDeNegocio:
    def test_faixas_de_desconto(self):
        """Regra de negócio testável sem HTTP e sem banco."""
        from src.services.relatorio_service import RelatorioService

        calcular = RelatorioService.calcular_desconto

        assert calcular(500) == 0.0
        assert calcular(2_000) == 40.0
        assert calcular(6_000) == 300.0
        assert calcular(20_000) == 2_000.0


class TestCadastroDeUsuario:
    def test_email_duplicado_retorna_409(self, client):
        payload = {
            "nome": "Duplicado",
            "email": "duplicado@teste.com",
            "senha": "senha-forte-de-teste",
        }
        assert client.post("/usuarios", json=payload).status_code == 201
        assert client.post("/usuarios", json=payload).status_code == 409

    def test_email_invalido_retorna_400(self, client):
        resposta = client.post(
            "/usuarios",
            json={"nome": "X", "email": "nao-e-email", "senha": "senha-forte-de-teste"},
        )
        assert resposta.status_code == 400

    def test_senha_curta_retorna_400(self, client):
        resposta = client.post(
            "/usuarios", json={"nome": "Xis", "email": "x@teste.com", "senha": "123"}
        )
        assert resposta.status_code == 400

    def test_nao_e_possivel_se_cadastrar_como_admin(self, client):
        """O campo 'tipo' do payload é ignorado."""
        resposta = client.post(
            "/usuarios",
            json={
                "nome": "Escalada",
                "email": "escalada@teste.com",
                "senha": "senha-forte-de-teste",
                "tipo": "admin",
            },
        )
        assert resposta.status_code == 201
        assert resposta.get_json()["dados"]["tipo"] == "cliente"

    def test_corpo_invalido_retorna_400(self, client):
        assert client.post("/usuarios", json=[]).status_code == 400
        assert client.post("/usuarios").status_code == 400
