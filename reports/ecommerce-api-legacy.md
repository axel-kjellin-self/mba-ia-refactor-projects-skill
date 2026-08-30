# Architecture Audit Report — ecommerce-api-legacy

**Project:** ecommerce-api-legacy
**Stack:** JavaScript (Node.js 20, CommonJS) + Express 4.18.2 + sqlite3 5.1.6
**Files:** 3 analyzed (`src/app.js`, `src/AppManager.js`, `src/utils.js`) | ~180 lines of code
**Domain:** LMS / e-learning com fluxo de checkout (venda de cursos)
**Date:** 2026-08-30

---

## Análise do Projeto (Fase 1)

| Item | Valor |
|------|-------|
| Language | JavaScript (Node.js, CommonJS) |
| Framework | Express 4.18.2 |
| Dependencies | `express`, `sqlite3` — nenhuma lib de auth, hash, validação ou config |
| Architecture | Monolítico. Uma God Class (`AppManager`) concentra schema do DB, seeds, rotas HTTP, regra de negócio, pagamento e persistência. Config e "crypto" caseira em `utils.js` |
| DB tables | `users`, `courses`, `enrollments`, `payments`, `audit_logs` (SQLite `:memory:`) |
| Endpoints | `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id` |

---

## Summary

| Severidade | Quantidade |
|------------|-----------|
| CRITICAL | 5 |
| HIGH | 6 |
| MEDIUM | 5 |
| LOW | 4 |
| **Total** | **20** |

> **Nota:** as queries SQL do código legado já usam placeholders `?` corretamente —
> **não há SQL Injection** neste projeto. Os riscos críticos são secrets expostos,
> criptografia quebrada e ausência total de autenticação.

---

## Findings

### [CRITICAL] Hardcoded Credentials e Secrets de Produção

**File:** `src/utils.js:1-7`

**Description:** Objeto `config` com senha de banco, chave *live* do gateway de pagamento e usuário SMTP em texto plano no código-fonte versionado.

```js
const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br",
    port: 3000
};
```

**Impact:** Qualquer pessoa com acesso ao repositório tem a chave de produção do gateway — fraude financeira direta. Viola PCI-DSS 3.2 e 8.2. A chave permanece no histórico do git mesmo após remoção.

**Recommendation:** Mover para `.env` + `src/config/settings.js` lendo `process.env`; criar `.env.example` e `.gitignore`. **Rotacionar todas as chaves expostas.**

---

### [CRITICAL] Dados de Cartão de Crédito em Log, junto com a Chave do Gateway

**File:** `src/AppManager.js:45`

**Description:** O número completo do cartão do cliente e a chave secreta do gateway são impressos no stdout a cada checkout.

```js
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

**Impact:** Violação direta de PCI-DSS 3.4 (proibido armazenar PAN em claro). Qualquer agregador de logs vira um repositório de cartões roubados.

**Recommendation:** Nunca logar PAN nem secrets. Logar apenas os 4 últimos dígitos via logger estruturado, com o gateway isolado num serviço dedicado.

---

### [CRITICAL] Criptografia Caseira e Quebrada para Senhas

**File:** `src/utils.js:17-23` (uso em `src/AppManager.js:68`)

**Description:** `badCrypto` concatena base64 do password 10.000× e devolve os 10 primeiros chars. Base64 é *encoding*, não hash; não há salt; o resultado depende apenas dos 2 primeiros caracteres do base64 — o espaço de saída é minúsculo e trivialmente reversível.

```js
function badCrypto(pwd) {
    let hash = "";
    for (let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

**Impact:** Colisões em massa e reversão instantânea. Um vazamento do banco expõe todas as senhas.

**Recommendation:** Substituir por `bcrypt` (cost ≥ 12) ou `argon2id`, com verificação via `bcrypt.compare`.

---

### [CRITICAL] Senha em Texto Plano no Seed

**File:** `src/AppManager.js:18`

**Description:** `INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')` — senha literal, sem hash, e ainda trivial.

**Impact:** O usuário semente entra no mesmo fluxo de autenticação dos demais; a senha `123` é adivinhada em uma tentativa.

**Recommendation:** Gerar hash bcrypt no seed e usar senha forte vinda de variável de ambiente em ambientes não-locais.

---

### [CRITICAL] Endpoint Destrutivo e Endpoint Admin sem Autenticação

**File:** `src/AppManager.js:80` (financial-report), `src/AppManager.js:131-137` (delete user)

**Description:** `GET /api/admin/financial-report` expõe receita e a lista de nomes/valores de todos os alunos publicamente. `DELETE /api/users/:id` apaga qualquer usuário sem nenhuma verificação — não há auth, não há autorização, não há ownership check.

**Impact:** Vazamento de dados pessoais e financeiros (LGPD/GDPR) e destruição de dados por qualquer anônimo na internet.

**Recommendation:** Middleware de autenticação JWT + checagem de papel `admin` em todas as rotas administrativas; `DELETE` restrito a admin ou ao próprio dono do recurso.

---

### [HIGH] God Class — Toda a Aplicação em uma Classe

**File:** `src/AppManager.js:4-141`

**Description:** `AppManager` acumula: conexão com o banco, DDL, seeds, definição de rotas HTTP, validação, regra de negócio de pagamento, persistência, auditoria e cache. Cinco domínios (users, courses, enrollments, payments, audit) no mesmo arquivo.

**Impact:** Impossível testar qualquer regra sem subir Express e SQLite. Toda mudança toca o mesmo arquivo — alto risco de regressão.

**Recommendation:** Separar em `models/` (repositories por entidade), `services/` (CheckoutService, ReportService, PaymentGateway), `controllers/`, `routes/`, `config/`.

---

### [HIGH] Callback Hell — 6 Níveis de Aninhamento

**File:** `src/AppManager.js:37-77` e `src/AppManager.js:83-128`

**Description:** Pirâmide de callbacks aninhados: `db.get` → `db.get` → `db.run` → `db.run` → `db.run` → callback final. O relatório aninha `forEach` dentro de `forEach` com contadores manuais (`coursesPending`, `enrPending`) simulando `Promise.all`.

**Impact:** Fluxo de erro inconsistente, código ilegível, contadores manuais são fonte clássica de bugs de concorrência.

**Recommendation:** Promisificar o driver (`util.promisify` ou wrapper próprio) e reescrever com `async/await`.

---

### [HIGH] N+1 Query Problem no Relatório Financeiro

**File:** `src/AppManager.js:83-128`

**Description:** Para cada curso, uma query de matrículas; para cada matrícula, duas queries (usuário e pagamento).

**Impact:** Com 50 cursos × 100 matrículas → 1 + 50 + 10.000 = **10.051 queries** para um único GET. O endpoint trava o processo sob carga real.

**Recommendation:** Uma única query com JOINs:

```sql
SELECT c.title, u.name, p.amount, p.status
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.id
LEFT JOIN users u       ON u.id = e.user_id
LEFT JOIN payments p    ON p.enrollment_id = e.id
```

---

### [HIGH] Lógica de Negócio dentro dos Route Handlers

**File:** `src/AppManager.js:28-137`

**Description:** Decisão de aprovação de pagamento, criação implícita de usuário, cálculo de receita e montagem do relatório vivem dentro dos handlers Express. Não existe camada de serviço.

**Impact:** Regra de negócio não reutilizável nem testável sem HTTP; duplicação inevitável quando surgir um segundo canal (CLI, worker).

**Recommendation:** Extrair `CheckoutService.execute()` e `ReportService.buildFinancialReport()`, sem qualquer dependência de `req`/`res`.

---

### [HIGH] Tratamento de Erro Inadequado e Silenciado

**File:** `src/AppManager.js:41, 57-58, 84, 92, 104-106, 133-135`

**Description:** Erros são engolidos em vários pontos: o callback do `audit_logs` (linha 57) recebe `err` e o ignora; os callbacks de `users` e `payments` no relatório (104, 106) nem checam `err`; o `DELETE` (133) ignora o erro e sempre responde 200. Mensagens são strings soltas e o logging é `console.log`.

**Impact:** Falhas silenciosas — cliente recebe sucesso enquanto o dado não foi gravado. Debug em produção é impossível.

**Recommendation:** Middleware de error handling centralizado, `next(err)` nos controllers, logger estruturado, respostas JSON padronizadas.

---

### [HIGH] Estado Global Mutável Compartilhado

**File:** `src/utils.js:9-10, 25` (uso em `src/AppManager.js:59`)

**Description:** `globalCache` e `totalRevenue` são singletons mutáveis exportados. Além disso `totalRevenue` é exportado por valor (número) — reatribuições nunca se propagam, tornando-o dead code enganoso. O cache cresce sem limite nem TTL.

**Impact:** Memory leak, estado compartilhado entre requisições, impossível escalar horizontalmente ou testar isoladamente.

**Recommendation:** Remover o estado global; usar cache com TTL/limite injetado como dependência, ou eliminá-lo.

---

### [MEDIUM] Ausência de Transação no Checkout

**File:** `src/AppManager.js:50-62`

**Description:** `INSERT enrollments` → `INSERT payments` → `INSERT audit_logs` executam sem `BEGIN TRANSACTION`/`COMMIT`. Se o insert de pagamento falhar, a matrícula já gravada permanece órfã.

**Impact:** Aluno matriculado sem pagamento registrado (ou o inverso) — inconsistência financeira direta.

**Recommendation:** Envolver as três operações em transação com rollback em qualquer falha.

---

### [MEDIUM] Registros Órfãos ao Deletar Usuário

**File:** `src/AppManager.js:131-137`

**Description:** O próprio código admite o problema na resposta: *"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."* Não há cascade nem limpeza.

**Impact:** Relatórios financeiros passam a contar matrículas de usuários inexistentes (`'Unknown'` na linha 113).

**Recommendation:** Soft delete, ou transação apagando dependentes, ou `FOREIGN KEY ... ON DELETE CASCADE` com `PRAGMA foreign_keys = ON`.

---

### [MEDIUM] Schema sem Foreign Keys e sem Constraints

**File:** `src/AppManager.js:12-16`

**Description:** Nenhuma tabela declara `FOREIGN KEY`, `NOT NULL` ou `UNIQUE`. `users.email` aceita duplicatas — o que quebra a busca por email na linha 40, que assume unicidade.

**Impact:** Integridade referencial inexistente; duas contas com o mesmo email tornam o login ambíguo.

**Recommendation:** Adicionar `email TEXT NOT NULL UNIQUE`, `NOT NULL` nos obrigatórios, FKs com `ON DELETE`, e habilitar `PRAGMA foreign_keys = ON`.

---

### [MEDIUM] Validação de Input Ausente ou Superficial

**File:** `src/AppManager.js:35` (e fallback em `:68`)

**Description:** A checagem é apenas de presença (`!u || !e || !cid || !cc`). Não valida formato de email, não valida que `c_id` é numérico, não valida o cartão, e a senha é opcional — o fallback silencioso `p || "123456"` cria contas com senha padrão conhecida.

**Impact:** Contas criadas com senha `123456` sem o usuário saber; dados inválidos no banco; `cc.startsWith` quebra se `card` não for string.

**Recommendation:** Schema validation (zod/joi) na borda do controller; tornar a senha obrigatória e aplicar política mínima de complexidade.

---

### [MEDIUM] Lógica de Pagamento Fake em Caminho de Produção

**File:** `src/AppManager.js:46`

**Description:** `let status = cc.startsWith("4") ? "PAID" : "DENIED";` — a aprovação depende do primeiro dígito do cartão, com a chave *live* do gateway carregada ao lado.

**Impact:** Qualquer cartão Visa inválido é aprovado; matrículas concedidas sem cobrança real.

**Recommendation:** Isolar atrás de uma interface `PaymentGateway` com implementação real e um `FakeGateway` restrito a desenvolvimento/testes.

---

### [LOW] Nomes de Variáveis e Contrato de API Crípticos

**File:** `src/AppManager.js:29-33`

**Description:** `u`, `e`, `p`, `cid`, `cc` no código; `usr`, `eml`, `pwd`, `c_id`, `card` no payload público da API.

**Impact:** Contrato de API confuso para consumidores; leitura do código exige decodificação mental.

**Recommendation:** `name`, `email`, `password`, `courseId`, `cardNumber` em ambos os lados (versionando a API se já houver consumidores).

---

### [LOW] Códigos HTTP e Respostas Inadequadas

**File:** `src/AppManager.js:35, 38, 48, 60, 135`

**Description:** Respostas em `text/plain` numa API JSON; pagamento recusado devolve 400 (deveria ser 402); erro de DB genérico devolve 500 sem código de erro; `DELETE` devolve 200 com texto humorístico em vez de 204.

**Impact:** Clientes não conseguem distinguir programaticamente os tipos de erro.

**Recommendation:** Padronizar `{ error: { code, message } }` em JSON, com 402 para recusa e 204 para delete.

---

### [LOW] Dead Code e Abstração Inútil

**File:** `src/utils.js:10, 12-15, 25`; `src/AppManager.js:2`

**Description:** `totalRevenue` é importado em `AppManager.js:2` e nunca usado. `logAndCache` mistura duas responsabilidades (log + cache) e alimenta um cache que ninguém lê.

**Impact:** Confusão sobre o que é usado de verdade; manutenção de código morto.

**Recommendation:** Remover `totalRevenue`, `globalCache` e `logAndCache`.

---

### [LOW] Ausência de `.gitignore`, `.env.example` e Documentação

**File:** raiz do projeto

**Description:** Não existe `.gitignore` (risco de commitar `node_modules` e futuros `.env`), nem `.env.example`, nem JSDoc. O README não documenta os endpoints nem o contrato de payload.

**Impact:** Onboarding custoso e risco de vazamento acidental de segredos.

**Recommendation:** Criar `.gitignore` e `.env.example`; documentar endpoints no README.

---

## Total: 20 findings

| # | Severidade | Finding | Arquivo |
|---|-----------|---------|---------|
| 1 | CRITICAL | Hardcoded credentials e secrets de produção | `src/utils.js:1-7` |
| 2 | CRITICAL | Cartão de crédito e chave do gateway em log | `src/AppManager.js:45` |
| 3 | CRITICAL | Criptografia caseira e quebrada para senhas | `src/utils.js:17-23` |
| 4 | CRITICAL | Senha em texto plano no seed | `src/AppManager.js:18` |
| 5 | CRITICAL | Endpoints admin e destrutivo sem autenticação | `src/AppManager.js:80, 131-137` |
| 6 | HIGH | God Class — toda a aplicação em uma classe | `src/AppManager.js:4-141` |
| 7 | HIGH | Callback hell — 6 níveis de aninhamento | `src/AppManager.js:37-77, 83-128` |
| 8 | HIGH | N+1 query problem no relatório financeiro | `src/AppManager.js:83-128` |
| 9 | HIGH | Lógica de negócio nos route handlers | `src/AppManager.js:28-137` |
| 10 | HIGH | Tratamento de erro inadequado e silenciado | `src/AppManager.js:41, 57, 104-106, 133` |
| 11 | HIGH | Estado global mutável compartilhado | `src/utils.js:9-10, 25` |
| 12 | MEDIUM | Ausência de transação no checkout | `src/AppManager.js:50-62` |
| 13 | MEDIUM | Registros órfãos ao deletar usuário | `src/AppManager.js:131-137` |
| 14 | MEDIUM | Schema sem foreign keys e constraints | `src/AppManager.js:12-16` |
| 15 | MEDIUM | Validação de input ausente ou superficial | `src/AppManager.js:35, 68` |
| 16 | MEDIUM | Lógica de pagamento fake em produção | `src/AppManager.js:46` |
| 17 | LOW | Nomes de variáveis e contrato de API crípticos | `src/AppManager.js:29-33` |
| 18 | LOW | Códigos HTTP e respostas inadequadas | `src/AppManager.js:35, 48, 60, 135` |
| 19 | LOW | Dead code e abstração inútil | `src/utils.js:10, 12-15` |
| 20 | LOW | Ausência de `.gitignore`, `.env.example` e docs | raiz |

---

## Status da Remediação (Fase 3)

Todos os 20 findings foram corrigidos na refatoração para MVC em camadas.

| Severidade | Correção aplicada |
|---|---|
| CRITICAL | Secrets → `.env` + validação fail-fast no boot; PAN mascarado e chave do gateway fora dos logs; `badCrypto` → bcrypt (12 rounds); seed com hash e senha via env; JWT + autorização por papel nas rotas admin/destrutivas |
| HIGH | God Class → 6 camadas (config/models/repositories/services/controllers/routes); callback hell → `async/await`; N+1 (~10.000 queries) → 1 query com JOINs; regra de negócio → services sem HTTP; error handler centralizado + logger JSON estruturado; estado global eliminado |
| MEDIUM | Transação com rollback no checkout; `ON DELETE CASCADE` + `PRAGMA foreign_keys = ON`; FKs/`NOT NULL`/`UNIQUE`/`CHECK`/índices; validação Zod na borda (senha obrigatória, mín. 12 chars); gateway atrás de interface `PaymentGateway` |
| LOW | Nomes descritivos no código e na API; JSON padronizado com status corretos (400/401/402/403/404/409/204); dead code removido; `.gitignore`, `.env.example` e README documentado |

**Validação:** 21 cenários testados end-to-end contra o servidor rodando — todos passaram, com 0 erros não tratados no log.

**Ações pendentes do time:**
1. **Rotacionar a chave `pk_live_1234567890abcdef`** — está no histórico do git e deve ser considerada comprometida.
2. Substituir o `FakePaymentGateway` (que aprova por `startsWith("4")`) por uma integração real antes de produção.
