# code-smells-project

API de E-commerce em Python/Flask, refatorada do monolito legado para uma
arquitetura MVC + Service Layer.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # ajuste SECRET_KEY e, em dev, SEED_ADMIN_*
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. Em desenvolvimento o schema é criado
no boot; em produção, rode `flask init-db` explicitamente e sirva via WSGI:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Testes

```bash
pytest tests/ -q
```

## Arquitetura

```
app.py                      # entry point (composition root fino)
src/
├── app_factory.py          # create_app(): fiação das camadas
├── config/
│   ├── settings.py         # carrega .env; falha o boot se faltar SECRET_KEY em prod
│   ├── database.py         # conexão por request (flask.g) + helper de transação
│   ├── schema.py           # DDL com FK/UNIQUE/CHECK/índices + seed
│   └── constants.py        # categorias, status, faixas de desconto, limites
├── models/                 # entidades + serialização (Produto, Usuario, Pedido)
├── repositories/           # SQL parametrizado, sem regra de negócio
├── services/               # regra de negócio pura, sem HTTP
├── controllers/            # tradução HTTP ↔ service
├── routes/                 # blueprints: URL → controller + guarda de acesso
├── middlewares/            # auth JWT, error handler global, logging
├── schemas/                # validação declarativa de payloads
└── utils/                  # exceções de domínio, bcrypt, JWT
```

Fluxo de uma request: `route → middleware de auth → controller → schema →
service → repository → banco`. Erros sobem como exceções de domínio e o error
handler global as traduz para o status HTTP correto.

## Autenticação

`POST /login` devolve um JWT. Envie-o como `Authorization: Bearer <token>`.

| Acesso | Endpoints |
|---|---|
| Público | `GET /`, `GET /health`, `GET /produtos*`, `POST /usuarios`, `POST /login` |
| Autenticado | `GET /me`, `POST /pedidos`, `GET /pedidos/usuario/<id>` (só os próprios), `GET /usuarios/<id>` (só o próprio) |
| Admin | `POST/PUT/DELETE /produtos`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas` |

## O que mudou em relação ao legado

**Segurança**
- 16 queries com concatenação de strings → 100% parametrizadas (login bypass e
  dump via `?q=' OR 1=1` deixaram de funcionar).
- `POST /admin/query` (execução de SQL arbitrário sem auth) e `POST /admin/reset-db`
  foram removidos.
- Senhas em texto plano → bcrypt; login com comparação de tempo constante.
- `SECRET_KEY` hardcoded → variável de ambiente, obrigatória em produção.
- `/health` não devolve mais `secret_key`/`debug`/`db_path`; `GET /usuarios` não
  devolve mais o campo `senha`.
- JWT com `login_required`/`admin_required` e checagem de ownership em pedidos
  (o IDOR de `/pedidos/usuario/<id>` foi fechado).

**Arquitetura**
- `models.py` (315 linhas, 4 domínios) e `controllers.py` (293 linhas) → camadas
  separadas por domínio.
- Regra de negócio (desconto, total, estoque) saiu da camada de dados e do HTTP;
  `calcular_desconto` é testável sem banco.
- Conexão global compartilhada entre threads → conexão por request.

**Correção e performance**
- Listagem de pedidos: de `1 + N + (N × M)` queries para 2 queries com JOIN.
- Criação de pedido em transação com débito atômico de estoque
  (`UPDATE ... WHERE estoque >= ?`), eliminando a race condition.
- Cancelamento agora devolve o estoque de fato (o legado só logava a intenção).
- Schema com FOREIGN KEYs, `UNIQUE(email)`, `NOT NULL`, `CHECK` e índices.
- Validação declarativa: input malformado retorna 400 em vez de 500.
- `print()` → `logging`; `except Exception` por endpoint → error handler global.
- Paginação (`?pagina=&por_pagina=`) em todas as listagens.

O banco legado foi preservado em `loja.db.legacy.bak` — o schema antigo e as
senhas em texto plano são incompatíveis com o novo formato.
