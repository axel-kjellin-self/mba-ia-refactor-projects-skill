# code-smells-project

API de E-commerce em Python/Flask, refatorada do monolito original para uma
arquitetura MVC em camadas (MVCS).

## Como rodar

```bash
pip install -r requirements.txt

cp .env.example .env
# Gere a chave e cole em SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(48))"
# Defina também SEED_ADMIN_PASSWORD para que o admin de exemplo seja criado.

python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite é criado no primeiro
boot com o catálogo de exemplo. A aplicação **não inicia** sem `SECRET_KEY` — é
proposital: uma chave default previsível invalidaria toda a autenticação.

Em produção, use um servidor WSGI:

```bash
gunicorn "app:app"
```

## Testes

```bash
python -m pytest tests/ -q
```

## Autenticação

Todas as rotas de escrita exigem um token JWT obtido no login:

```bash
# 1. Obter o token
curl -X POST http://127.0.0.1:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@loja.com","senha":"<SEED_ADMIN_PASSWORD>"}'

# 2. Usar nas requisições seguintes
curl http://127.0.0.1:5000/usuarios -H "Authorization: Bearer <token>"
```

Usuários criados via `POST /usuarios` são sempre do tipo `cliente`; o campo
`tipo` no payload é ignorado.

## Endpoints

| Método | Rota | Acesso |
|--------|------|--------|
| GET | `/` | Público |
| GET | `/health` | Público |
| GET | `/produtos` | Público |
| GET | `/produtos/busca` | Público |
| GET | `/produtos/<id>` | Público |
| POST | `/produtos` | Admin |
| PUT | `/produtos/<id>` | Admin |
| DELETE | `/produtos/<id>` | Admin |
| POST | `/usuarios` | Público |
| POST | `/login` | Público |
| GET | `/usuarios` | Admin |
| GET | `/usuarios/<id>` | Próprio usuário ou admin |
| POST | `/pedidos` | Autenticado |
| GET | `/pedidos/<id>` | Dono do pedido ou admin |
| GET | `/pedidos` | Admin |
| GET | `/pedidos/usuario/<id>` | Próprio usuário ou admin |
| PUT | `/pedidos/<id>/status` | Admin |
| GET | `/relatorios/vendas` | Admin |

Listagens aceitam `?limite=` (máx. 200) e `?offset=`.

## Arquitetura

```
app.py                    Entry point
src/
├── app_factory.py        Composition root
├── config/               settings, database, schema, constants
├── models/               Entidades (Produto, Usuario, Pedido)
├── repositories/         Acesso a dados — SQL parametrizado
├── services/             Regra de negócio
├── controllers/          Orquestração HTTP
├── routes/               Blueprints por domínio
├── middlewares/          auth (JWT), error_handler, logging
├── schemas/              Validação de entrada
└── utils/                errors, security
tests/                    Testes de integração
```

Fluxo de um request:

```
Route → Middleware de auth → Controller → Schema → Service → Repository → Model
```

Regra de dependência: cada camada só conhece a camada imediatamente abaixo.
Services não importam Flask; Repositories não conhecem regra de negócio.

## Notas de segurança

- Senhas são armazenadas com **bcrypt** (custo 12) e nunca aparecem em respostas.
- Todas as queries são **parametrizadas**; os curingas do `LIKE` são escapados.
- Os endpoints `POST /admin/query` e `POST /admin/reset-db` foram **removidos**.
- `SECRET_KEY` vem do ambiente e o boot falha se ela estiver ausente ou for curta.
- CORS restrito às origens de `CORS_ORIGINS`.
- `/health` expõe apenas status e conectividade do banco.

## Migração a partir da versão anterior

O schema mudou: a coluna `usuarios.senha` (texto plano) virou `usuarios.senha_hash`,
e foram adicionadas constraints e foreign keys. Um `loja.db` gerado pela versão
antiga **não é compatível** — apague-o e deixe a aplicação recriá-lo, ou escreva
uma migração que force a redefinição de senha de todos os usuários (os hashes não
podem ser derivados das senhas antigas sem conhecê-las... que, no caso, estavam
todas em claro no banco e devem ser consideradas comprometidas).
