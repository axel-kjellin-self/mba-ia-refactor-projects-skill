# task-manager-api

API de Task Manager em Python/Flask, refatorada para MVC + Service Layer pela skill `refactor-arch`.

O relatório da auditoria que motivou a refatoração está em [`../reports/task-manager-api.md`](../reports/task-manager-api.md).

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Gere e preencha SECRET_KEY e SEED_PASSWORD:
python -c "import secrets; print(secrets.token_urlsafe(48))"

python seed.py     # popula o banco (rode antes do primeiro boot)
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. A app falha no boot se `SECRET_KEY` não estiver definida.

## Arquitetura

```
app.py                      # entry point
src/
├── app_factory.py          # application factory (composition root)
├── config/                 # settings (.env), database, constants
├── models/                 # entidades SQLAlchemy
├── repositories/           # acesso a dados (queries, agregações)
├── services/               # regras de negócio, sem HTTP
├── controllers/            # orquestração HTTP (request → service → response)
├── routes/                 # mapeamento URL → controller + middlewares
├── schemas/                # validação (marshmallow) e serialização
├── middlewares/            # auth JWT, error handler, logging
└── utils/                  # exceções de domínio, helpers
```

Fluxo: `route → middleware de auth → controller → service → repository → model`.

## Autenticação

Todos os endpoints exigem JWT, exceto `/`, `/health`, `POST /login` e `POST /users` (registro).

```bash
TOKEN=$(curl -s -X POST localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"joao@email.com","password":"'"$SEED_PASSWORD"'"}' | jq -r .token)

curl localhost:5000/tasks -H "Authorization: Bearer $TOKEN"
```

O token expira em `JWT_EXPIRES_SECONDS` (default 3600s).

## Endpoints

| Método | Rota | Autorização |
|---|---|---|
| GET | `/` | pública |
| GET | `/health` | pública |
| POST | `/login` | pública |
| POST | `/users` | pública (registro) |
| GET | `/users` | admin, manager |
| GET | `/users/<id>` | próprio, admin, manager |
| PUT | `/users/<id>` | próprio, admin |
| DELETE | `/users/<id>` | admin |
| GET | `/users/<id>/tasks` | próprio, admin, manager |
| GET | `/tasks` | autenticado |
| GET | `/tasks/<id>` | autenticado |
| POST | `/tasks` | autenticado |
| PUT | `/tasks/<id>` | autenticado |
| DELETE | `/tasks/<id>` | admin, manager |
| GET | `/tasks/search` | autenticado |
| GET | `/tasks/stats` | autenticado |
| GET | `/categories` | autenticado |
| POST | `/categories` | admin, manager |
| PUT | `/categories/<id>` | admin, manager |
| DELETE | `/categories/<id>` | admin |
| GET | `/reports/summary` | admin, manager |
| GET | `/reports/user/<id>` | próprio, admin, manager |

`GET /tasks/search` aceita `?q=&status=&priority=&user_id=`.

## Variáveis de ambiente

Veja `.env.example`. Obrigatória: `SECRET_KEY`. O `.env` não é versionado.

## Códigos de resposta

Tratados centralmente em `src/middlewares/error_handler.py`:

| Situação | Status |
|---|---|
| Falha de schema / input inválido | 400 |
| Token ausente, inválido ou expirado | 401 |
| Autenticado sem permissão | 403 |
| Recurso inexistente | 404 |
| Conflito de unicidade | 409 |
| Erro inesperado (logado, sem vazar detalhes) | 500 |
