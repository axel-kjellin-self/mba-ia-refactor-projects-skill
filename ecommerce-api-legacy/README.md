# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada de um monolito de
3 arquivos para uma arquitetura MVC em camadas.

## Como rodar

```bash
npm install
cp .env.example .env
# Gere um segredo forte para o JWT:
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
# Cole o resultado em JWT_SECRET no .env
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória por
padrão (`DATABASE_FILE=:memory:`) e carrega seeds no boot.

Exemplos de requisições estão em `api.http`.

## Arquitetura

```
server.js                    Entry point: valida config, conecta ao banco, sobe o servidor
src/
├── app.js                   Application factory (Express)
├── container.js             Composition root — monta o grafo de dependências
├── config/
│   ├── index.js             Configuração via variáveis de ambiente + fail-fast
│   ├── constants.js         Constantes de domínio (status, roles, regras)
│   └── database.js          Wrapper Promise sobre sqlite3, com transações
├── models/
│   └── schema.js            DDL (FKs, constraints, índices) e seeds
├── repositories/            Acesso a dados — uma classe por entidade
├── services/                Regra de negócio pura (sem HTTP)
│   └── PaymentGateway.js    Fronteira com o provedor de pagamento
├── controllers/             Orquestração HTTP (request → service → response)
├── routes/                  Mapeamento URL → middleware → controller
├── middlewares/             auth, validate, errorHandler, requestLogger
├── validators/              Schemas Zod de validação de input
└── utils/                   logger estruturado, hierarquia de erros
```

**Fluxo de um request:** `routes` → `validate` → `auth` → `controller` →
`service` → `repository` → `database`. Erros sobem via `next(err)` até o
`errorHandler` central, que traduz a exceção em status code e corpo JSON.

## Endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/health` | — | Health check |
| POST | `/api/auth/login` | — | Autentica e retorna um JWT |
| POST | `/api/checkout` | — | Cadastro + compra de curso |
| GET | `/api/admin/financial-report` | admin | Receita e alunos por curso |
| GET | `/api/users/:id` | dono ou admin | Dados do usuário |
| DELETE | `/api/users/:id` | dono ou admin | Remove usuário e dados associados |

Autenticação via header `Authorization: Bearer <token>`.

### Formato de erro

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados inválidos",
    "details": [{ "field": "password", "message": "A senha deve ter no mínimo 12 caracteres" }]
  }
}
```

Status usados: `400` validação, `401` não autenticado, `402` pagamento recusado,
`403` sem permissão, `404` não encontrado, `409` conflito, `500` erro interno.

## Configuração

Todos os secrets vêm de variáveis de ambiente — ver `.env.example`. A aplicação
**não inicia** se `JWT_SECRET` ou `PAYMENT_GATEWAY_KEY` estiverem ausentes, ou se
o segredo JWT tiver menos de 32 caracteres.

O `.env` está no `.gitignore` e nunca deve ser commitado.

## Notas de segurança

- Senhas com **bcrypt** (12 rounds). O hash nunca aparece em respostas de API.
- Número de cartão nunca é logado por completo — apenas os 4 últimos dígitos
  (PCI-DSS 3.4). A chave do gateway jamais vai para o log.
- Rotas administrativas e destrutivas exigem JWT válido e autorização por papel.
- `PRAGMA foreign_keys = ON` com `ON DELETE CASCADE`: deletar um usuário remove
  suas matrículas e pagamentos, sem deixar registros órfãos.
- Checkout grava matrícula, pagamento e auditoria em uma única transação.

> O `FakePaymentGateway` aprova cartões iniciados em `4`. É uma implementação de
> desenvolvimento — substitua por um gateway real antes de ir a produção.
