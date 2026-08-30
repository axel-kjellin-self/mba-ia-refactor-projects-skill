# ARCHITECTURE AUDIT REPORT

**Project:** code-smells-project
**Stack:** Python 3.12 + Flask 3.1.1 (flask-cors 5.0.1, SQLite3)
**Files:** 4 source files analyzed | ~780 lines of code
**Date:** 2026-08-30

## Summary

| CRITICAL | HIGH | MEDIUM | LOW |
|----------|------|--------|-----|
| 6 | 5 | 6 | 4 |

**Total: 21 findings**

---

## CRITICAL

### [CRITICAL] SQL Injection generalizado (18 pontos de injeção)

**File:** `models.py:28, 48-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 279-281, 289-299`

**Description:** Praticamente TODAS as queries em `models.py` são construídas por concatenação de strings com input do usuário. Não há uma única query parametrizada na camada de acesso a dados (apenas o seed em `database.py:70-83` usa `?`).

```python
# models.py:109-111 — login
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)

# models.py:28
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

# models.py:291 — busca com LIKE
query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
```

**Attack vectors:**
- Bypass de login: `email = "admin@loja.com' --"` → autentica como admin sem senha
- Exfiltração: `GET /produtos/busca?categoria=' UNION SELECT id,nome,email,senha,tipo,criado_em,1,1 FROM usuarios --`
- Destruição: `nome = "x'); DROP TABLE produtos; --"` no POST /produtos

**Impact:** Comprometimento total do banco. Leitura, alteração e exclusão de qualquer dado sem autenticação. OWASP A03:2021.

**Recommendation:** Substituir 100% das queries por parametrizadas (`cursor.execute("... WHERE id = ?", (id,))`). Para a busca dinâmica, montar a lista de cláusulas com placeholders e acumular params numa tupla.

---

### [CRITICAL] Endpoint de execução de SQL arbitrário sem autenticação

**File:** `app.py:59-78`

**Description:** `POST /admin/query` recebe SQL cru no corpo do request e o executa contra o banco, retornando o resultado. Sem autenticação, sem autorização, sem allowlist.

```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query)
```

**Impact:** RCE-equivalente no nível de banco de dados. Qualquer pessoa na rede pode ler senhas, criar usuários admin, ou apagar tudo. Com `CORS(app)` sem restrição de origem (`app.py:9`), qualquer site pode disparar isso do navegador da vítima.

**Recommendation:** Remover o endpoint. Se um console administrativo for realmente necessário, expô-lo fora da API pública, atrás de autenticação + role admin + auditoria.

---

### [CRITICAL] Endpoint destrutivo `/admin/reset-db` sem autenticação

**File:** `app.py:47-57`

**Description:** `POST /admin/reset-db` apaga todas as linhas de `itens_pedido`, `pedidos`, `produtos` e `usuarios`. Nenhuma verificação de identidade ou permissão.

**Impact:** Perda total e irreversível de dados por um único request não autenticado. Combinado com CORS aberto, é explorável via CSRF.

**Recommendation:** Remover da aplicação. Reset de base pertence a um script de CLI/seed, não a uma rota HTTP. Se mantido para dev, guardar atrás de `@require_admin` e habilitar somente quando `ENV != production`.

---

### [CRITICAL] Senhas armazenadas e comparadas em texto plano

**File:** `models.py:105-131`, `database.py:30, 75-83`

**Description:** Senhas são gravadas no INSERT sem qualquer hash (`models.py:126-129`) e a autenticação é feita comparando a senha crua dentro do WHERE (`models.py:109-111`). O seed grava `admin123`, `123456`, `senha123` em claro (`database.py:76-78`).

**Impact:** Qualquer leitura do arquivo `loja.db` (ou do `/usuarios`, ver abaixo) expõe as credenciais de todos os usuários. Como usuários reutilizam senhas, o impacto vaza para outros sistemas. Violação de LGPD/GDPR e PCI-DSS.

**Recommendation:** Hash com bcrypt (`bcrypt.hashpw` no cadastro, `bcrypt.checkpw` no login). Nunca colocar a senha na cláusula WHERE — buscar por email e verificar o hash em memória.

---

### [CRITICAL] Endpoint público expõe hashes/senhas de todos os usuários

**File:** `models.py:79-86, 95-102`, `controllers.py:128-144`, `app.py:18-19`

**Description:** `get_todos_usuarios()` e `get_usuario_por_id()` incluem o campo `senha` no dicionário serializado, e `GET /usuarios` / `GET /usuarios/<id>` devolvem isso diretamente, sem autenticação.

```python
result.append({ ..., "senha": row["senha"], ... })   # models.py:83
```

**Impact:** `curl http://host/usuarios` entrega nome, email, senha e tipo de todos os usuários — inclusive do admin. É o vazamento mais direto possível.

**Recommendation:** Nunca selecionar/serializar `senha` fora do fluxo de autenticação. Criar um serializer explícito com allowlist de campos e proteger a rota com autenticação + checagem de role.

---

### [CRITICAL] SECRET_KEY hardcoded e exposta no /health

**File:** `app.py:7`, `controllers.py:285-289`

**Description:** A chave de assinatura da aplicação está literal no código (`"minha-chave-super-secreta-123"`) e é devolvida pelo endpoint público `/health`, junto com `debug: True`, `ambiente: producao` e `db_path`.

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"     # app.py:7
...
"secret_key": "minha-chave-super-secreta-123"                  # controllers.py:289
```

**Impact:** Permite forjar sessões/tokens assinados. Estando no git, a chave já deve ser considerada comprometida permanentemente. O health check ainda entrega o mapa do sistema para o atacante.

**Recommendation:** Carregar de variável de ambiente (`os.environ["SECRET_KEY"]`, falhando o boot se ausente), adicionar `.env` ao `.gitignore`, criar `.env.example`, rotacionar a chave. O `/health` deve devolver apenas `status` e conectividade do banco.

---

## HIGH

### [HIGH] Ausência total de autenticação e autorização

**File:** `app.py:11-30, 47-78`, `controllers.py:167-186`

**Description:** Nenhuma rota exige autenticação. O `login` valida credenciais mas não emite token nem sessão — retorna apenas os dados do usuário, então não existe nada que rotas subsequentes possam verificar. Operações de escrita (criar/atualizar/deletar produto, mudar status de pedido) e leitura de dados alheios (`GET /pedidos/usuario/<id>`) são abertas.

**Impact:** Qualquer cliente altera preços, zera estoque, deleta produtos, aprova pedidos e lê o histórico de compras de qualquer usuário (IDOR). Não há distinção entre admin e cliente, embora o campo `tipo` exista no schema.

**Recommendation:** Emitir JWT no login (PyJWT já está no venv), criar middleware `@require_auth` / `@require_role("admin")`, aplicar nas rotas de escrita e admin, e validar ownership em `/pedidos/usuario/<id>`.

---

### [HIGH] God Modules — arquitetura sem camadas

**File:** `models.py:1-315`, `controllers.py:1-293`, `app.py:1-88`

**Description:** Três arquivos concentram todos os domínios (produtos, usuários, pedidos, relatórios). `models.py` mistura acesso a dados, regra de negócio (cálculo de total, checagem de estoque, faixas de desconto) e serialização. `controllers.py` mistura validação, regra de negócio, notificação e formatação HTTP. `app.py` registra rotas *e* implementa handlers com SQL inline.

**Impact:** Impossível testar regra de negócio sem subir Flask e sem banco real. Qualquer mudança em produtos arrisca quebrar pedidos. Nenhuma camada é reutilizável ou substituível.

**Recommendation:** Estruturar em `src/{config,models,repositories,services,controllers,routes,middlewares,schemas}` com um módulo por domínio.

---

### [HIGH] N+1 Queries na listagem de pedidos

**File:** `models.py:171-201` e `models.py:203-233`

**Description:** Para cada pedido busca-se os itens (1 query), e para cada item busca-se o nome do produto (1 query). Ambas as funções duplicam exatamente o mesmo laço aninhado.

```python
for row in rows:                                   # N pedidos
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + ...)
    for item in itens:                             # M itens
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + ...)
```

**Impact:** 100 pedidos com 3 itens cada = 1 + 100 + 300 = **401 queries** em `GET /pedidos`. Sem paginação, o custo cresce sem limite com o volume de dados.

**Recommendation:** Uma query com JOIN (`pedidos` ⨝ `itens_pedido` ⨝ `produtos`) agrupada em memória, ou duas queries com `WHERE pedido_id IN (...)`. Adicionar paginação (`LIMIT`/`OFFSET`).

---

### [HIGH] Regra de negócio espalhada entre models e controllers

**File:** `models.py:133-169, 235-273`, `controllers.py:43-54, 188-220, 237-255`

**Description:** Cálculo de total do pedido, validação de estoque e faixas de desconto vivem em `models.py`; validação de faixa de preço, categorias válidas, status válidos e disparo de notificações vivem em `controllers.py`. `criar_pedido` retorna `{"erro": ...}` como valor de retorno, forçando o controller a inspecionar dicionário para decidir o HTTP status (`controllers.py:205`).

**Impact:** A mesma regra precisa ser reimplementada em qualquer novo canal (CLI, worker, outro endpoint). Erros de domínio trafegam como dados, não como exceções, o que silencia falhas facilmente.

**Recommendation:** Camada `services/` com regras puras, levantando exceções de domínio (`EstoqueInsuficienteError`, `ProdutoNaoEncontradoError`) traduzidas para HTTP por um error handler central.

---

### [HIGH] Tratamento de erro impróprio e uso de `print` como log

**File:** `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 291-292`; `app.py:56, 77-78, 83-86`

**Description:** Todo handler repete o mesmo `try/except Exception` que devolve `str(e)` ao cliente com HTTP 500. Erros de validação (ex.: `preco` não numérico em `controllers.py:43`, `float()` inválido em `controllers.py:119`) caem no except genérico e viram 500 em vez de 400. O logging é feito com `print()` — 14 ocorrências, sem nível, sem timestamp, sem correlação.

**Impact:** Mensagens internas (incluindo trechos de SQL) vazam para o cliente, ajudando a explorar a injeção. Em produção, `print` sem estrutura torna o diagnóstico inviável.

**Recommendation:** Error handler global (`@app.errorhandler`) mapeando exceções de domínio → status, resposta genérica para 500, e `logging` configurado com nível/formato.

---

## MEDIUM

### [MEDIUM] Falta de transação em `criar_pedido`

**File:** `models.py:133-169`

**Description:** O pedido, seus itens e as baixas de estoque são inseridos em múltiplos `execute()` com um único `commit()` no fim, mas sem `try/rollback`. Se um item falhar no meio (produto removido concorrentemente, erro de constraint), a exceção sobe e o `commit` não ocorre — porém a conexão global permanece com a transação suja, e um `commit()` de outra requisição a persiste parcialmente.

**Impact:** Pedidos com itens faltando e estoque decrementado incorretamente. Como a conexão é global e compartilhada entre threads, o risco é real sob concorrência.

**Recommendation:** Bloco explícito `try/except` com `db.rollback()`, e conexão por request em vez de global.

---

### [MEDIUM] Conexão SQLite global compartilhada entre threads

**File:** `database.py:4-11`, usada em todos os módulos

**Description:** Uma única conexão em variável global com `check_same_thread=False`, reutilizada por todas as requisições do servidor multi-thread do Flask.

**Impact:** Cursors e transações se misturam entre requisições concorrentes; commits de uma request persistem escritas parciais de outra. Erros do tipo "database is locked" e corrupção lógica de dados.

**Recommendation:** Conexão por request via `flask.g` + `teardown_appcontext`, com a criação de schema movida para uma função de inicialização explícita.

---

### [MEDIUM] Validação de entrada ausente ou inconsistente

**File:** `controllers.py:24-62, 64-96, 111-126, 146-165, 188-220, 237-255`

**Description:** `criar_produto` valida presença e faixa mas não valida tipo — `{"preco": "abc"}` passa pelo `if preco < 0` com TypeError → 500. `atualizar_produto` não valida categoria (o `criar` valida). `criar_usuario` não valida formato de email nem duplicidade. `criar_pedido` não verifica se `usuario_id` existe, nem se `quantidade` é inteiro positivo — `quantidade: -5` **aumenta** o estoque e reduz o total. `buscar_produtos` faz `float()` sem try (`controllers.py:118-121`).

**Impact:** Dados corrompidos no banco, 500s em entradas triviais, e um bug de negócio explorável (quantidade negativa gera pedido de valor negativo).

**Recommendation:** Schemas de validação por endpoint (`schemas/`), com tipo, faixa e formato, executados antes de chegar ao service.

---

### [MEDIUM] Schema sem constraints, foreign keys ou índices

**File:** `database.py:14-53`

**Description:** Nenhuma coluna é `NOT NULL`, `usuarios.email` não é `UNIQUE`, `pedidos.usuario_id` / `itens_pedido.pedido_id` / `itens_pedido.produto_id` não são FOREIGN KEY, não há CHECK em `preco`/`estoque`/`status`, e não há índice nas colunas de junção.

**Impact:** Emails duplicados, pedidos órfãos apontando para usuários inexistentes, registros com campos nulos, e full scans nas consultas de itens.

**Recommendation:** Adicionar `NOT NULL`, `UNIQUE(email)`, `FOREIGN KEY ... REFERENCES`, `CHECK (preco >= 0)`, `CHECK (status IN (...))`, índices em `itens_pedido(pedido_id)` e `pedidos(usuario_id)`, e habilitar `PRAGMA foreign_keys = ON`.

---

### [MEDIUM] DEBUG habilitado e CORS totalmente aberto

**File:** `app.py:8, 9, 88`

**Description:** `DEBUG = True` fixo no código e `app.run(debug=True)` expõem o console interativo do Werkzeug. `CORS(app)` sem parâmetros libera qualquer origem.

**Impact:** O debugger do Werkzeug permite execução de código Python arbitrário no servidor. CORS aberto permite que qualquer site invoque `/admin/reset-db` e `/admin/query` com o navegador da vítima.

**Recommendation:** `DEBUG` vindo de env (default `False`), CORS restrito a uma lista de origens configurável, e servidor WSGI de produção (gunicorn) em vez de `app.run`.

---

### [MEDIUM] Duplicação de código

**File:** `models.py:9-22 / 30-40 / 302-313` (serialização de produto ×3), `models.py:171-201 / 203-233` (montagem de pedido ×2), `models.py:79-86 / 95-102` (serialização de usuário ×2), `controllers.py:28-50 / 72-90` (bloco de validação de produto ×2)

**Description:** Os mesmos blocos de serialização e validação aparecem repetidos, com divergências sutis (o `atualizar_produto` não valida categoria; o `buscar_produtos` repete os 8 campos).

**Impact:** Adicionar uma coluna a `produtos` exige editar 3 lugares; esquecer um gera resposta inconsistente entre endpoints — que é exatamente o que já aconteceu com a validação de categoria.

**Recommendation:** Um serializer por entidade e um validador por schema, reutilizados em todos os pontos.

---

## LOW

### [LOW] Magic numbers e strings

**File:** `models.py:256-262` (faixas 10000/5000/1000 e taxas 0.1/0.05/0.02), `controllers.py:47-52` (limites 2/200, lista de categorias), `controllers.py:242` (lista de status), `app.py:88` (porta 5000), `database.py:5` (`"loja.db"`)

**Description:** Regras de negócio expressas como literais espalhados, sem nome. As categorias válidas e os status válidos estão embutidos em condicionais dentro dos controllers.

**Impact:** A regra de desconto não é localizável por busca; alterar uma faixa exige entender o encadeamento de `elif`. Categorias e status podem divergir entre endpoints.

**Recommendation:** `config/constants.py` com `FAIXAS_DESCONTO`, `CATEGORIAS_VALIDAS`, `STATUS_PEDIDO`, e limites de nome.

---

### [LOW] Ausência de docstrings e type hints

**File:** todas as funções em `models.py`, `controllers.py`, `database.py`

**Description:** Nenhuma função possui docstring ou anotação de tipo. Parâmetros como `itens` (lista de dicionários com formato implícito) e retornos polimórficos (`criar_pedido` retorna sucesso ou erro no mesmo dicionário) não são documentados em lugar algum.

**Impact:** O contrato de cada função só é descobrível lendo a implementação; nenhuma verificação estática é possível.

**Recommendation:** Type hints em todas as assinaturas públicas e docstrings nos services, com `mypy` no CI.

---

### [LOW] Código morto e imports não utilizados

**File:** `models.py:2` (`import sqlite3` nunca usado), `database.py:2` (`import os` nunca usado), `controllers.py:3` (`from database import get_db` usado só pelo health check, que não deveria acessar o banco diretamente)

**Impact:** Ruído; sugere dependências que não existem.

**Recommendation:** Remover imports mortos; adicionar linter (ruff/flake8) ao fluxo.

---

### [LOW] Códigos HTTP inadequados

**File:** `controllers.py:60-62, 95-96, 125-126, 164-165, 218-220`; `app.py:77-78`

**Description:** Falhas de validação e de tipo retornam 500 por caírem no `except Exception` genérico. `criar_pedido` devolve 400 para "produto não encontrado" (deveria ser 404 ou 422). Nenhuma rota usa 401/403, já que não há autenticação.

**Impact:** Clientes não conseguem distinguir erro do próprio request de falha do servidor; retries automáticos ficam incorretos.

**Recommendation:** Mapear exceções de domínio para os status corretos no error handler central (400 validação, 401 não autenticado, 403 sem permissão, 404 inexistente, 409 conflito, 500 apenas para inesperado).

---

## Conclusão

O projeto está em estado **não deployável**. As 6 falhas CRITICAL formam uma cadeia completa de comprometimento: `/admin/query` dá acesso irrestrito ao banco, `GET /usuarios` entrega as senhas em claro, a SECRET_KEY está no repositório, e a SQL injection no login permite bypass de autenticação — que aliás não existe. O CORS aberto torna tudo isso explorável a partir do navegador de qualquer usuário.

Estruturalmente, os três arquivos não têm separação de responsabilidades: dados, regras e HTTP convivem nas mesmas funções, tornando a correção pontual de cada vulnerabilidade tão custosa quanto a reestruturação em camadas.

**Ordem de correção recomendada:** remover endpoints admin → parametrizar queries → hash de senhas + remoção do campo `senha` das respostas → externalizar config → introduzir autenticação → separar camadas → corrigir N+1 e transações → validação e constraints → limpeza de qualidade.
