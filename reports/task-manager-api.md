# Architecture Audit Report — task-manager-api

> Gerado pela skill `refactor-arch` (Fase 2 — Auditoria Arquitetural)
> Data: 2026-08-30

---

## Fase 1 — Análise do Projeto

| Campo | Valor |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | Flask 3.0.0 (+ Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0) |
| **Dependencies** | flask, flask-sqlalchemy, flask-cors, marshmallow (não usado), requests (não usado), python-dotenv (não usado), PyJWT (no `.venv`, ausente do `requirements.txt`) |
| **Domain** | Task Manager / Gestão de Tarefas (tasks, users, categories, reports) |
| **Architecture** | Pseudo-MVC. Existem pastas `models/`, `routes/`, `services/`, `utils/`, mas sem camadas de controllers/repositories/services reais. Toda a lógica de negócio vive nos Blueprints. Não há application factory, config externalizada, autenticação, nem error handling. |
| **Source files** | 14 arquivos Python (~1.158 linhas) |
| **DB tables** | `users`, `tasks`, `categories` (SQLite `tasks.db`) |
| **Endpoints** | 19 rotas — `/tasks` (CRUD, search, stats), `/users` (CRUD, tasks, login), `/categories` (CRUD), `/reports/summary`, `/reports/user/<id>`, `/health`, `/` |

---

## Summary

| Severidade | Quantidade |
|---|---|
| 🔴 CRITICAL | 5 |
| 🟠 HIGH | 6 |
| 🟡 MEDIUM | 7 |
| 🔵 LOW | 5 |
| **Total** | **23** |

---

## Findings

### [CRITICAL] Password Hashing com MD5 sem salt

**File:** `models/user.py:29, 32`

**Description:** `set_password()` usa `hashlib.md5(pwd.encode()).hexdigest()` e `check_password()` compara o mesmo MD5. MD5 é criptograficamente quebrado desde 2004, é extremamente rápido (bilhões de hashes/s em GPU) e não há salt — hashes idênticos para senhas idênticas.

**Impact:** Um dump do banco expõe todas as senhas em minutos via rainbow tables. Senhas do seed (`1234`, `abcd`, `pass`) caem instantaneamente.

**Recommendation:** Migrar para `werkzeug.security.generate_password_hash` / `check_password_hash` (pbkdf2-sha256) ou bcrypt.

```python
# models/user.py:29 — ANTES (quebrado)
self.password = hashlib.md5(pwd.encode()).hexdigest()

# DEPOIS (seguro)
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
```

---

### [CRITICAL] Hash de senha exposto em respostas da API

**File:** `models/user.py:21` (propagado para `routes/user_routes.py:33, 85, 129, 209`)

**Description:** `User.to_dict()` inclui o campo `password`. Esse dict é retornado por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.

**Impact:** Qualquer requisição anônima a `GET /users/1` devolve o hash MD5 de qualquer usuário — cracking offline sem precisar de breach do banco. Combinado com o finding anterior, é comprometimento total de contas. Violação de OWASP A02:2021 (Cryptographic Failures).

**Recommendation:** Remover `password` de `to_dict()` permanentemente; usar schemas de serialização (marshmallow já está nas dependências).

```python
# models/user.py:16-25 — o campo 'password' NUNCA deve sair da camada de dados
return {
    'id': self.id,
    'name': self.name,
    'email': self.email,
    'password': self.password,   # ← VAZAMENTO
    ...
}
```

---

### [CRITICAL] Hardcoded Secrets

**File:** `app.py:11-13`, `services/notification_service.py:7-10`

**Description:** `SECRET_KEY = 'super-secret-key-123'` e credenciais SMTP (`taskmanager@gmail.com` / `senha123`) hardcoded e versionadas no Git.

**Impact:** Secret previsível permite forjar sessões/tokens assinados. Credenciais SMTP no repositório permitem envio de e-mail em nome da aplicação (phishing). Violação de compliance (SOC2, PCI-DSS).

**Recommendation:** Extrair para `.env` + `config/settings.py` via `python-dotenv`; adicionar `.env` ao `.gitignore`; **rotacionar a senha SMTP exposta**.

```python
# app.py:13
app.config['SECRET_KEY'] = 'super-secret-key-123'

# services/notification_service.py:9-10
self.email_user = 'taskmanager@gmail.com'
self.email_password = 'senha123'
```

---

### [CRITICAL] Token de autenticação falso

**File:** `routes/user_routes.py:210`

**Description:** O login retorna `'token': 'fake-jwt-token-' + str(user.id)`. Não é assinado, não expira, e é trivialmente forjável (`fake-jwt-token-1` = admin).

**Impact:** Escalação de privilégios para qualquer atacante que adivinhe um ID. O token nem sequer é verificado em lugar algum — é puramente decorativo.

**Recommendation:** Emitir JWT real assinado com `SECRET_KEY` (PyJWT), com `exp` e claims `user_id`/`role`, e validá-lo em middleware.

---

### [CRITICAL] Endpoints destrutivos sem autenticação

**File:** `routes/user_routes.py:134-151`, `routes/task_routes.py:225-238`, `routes/report_routes.py:211-223`

**Description:** `DELETE /users/<id>`, `DELETE /tasks/<id>` e `DELETE /categories/<id>` são públicos. `DELETE /users/<id>` ainda apaga em cascata todas as tasks do usuário (linhas 140-142).

**Impact:** Qualquer pessoa com acesso de rede pode apagar toda a base de dados com um loop de `curl`. Perda total de dados.

**Recommendation:** Middleware `@require_auth` + `@require_role('admin')` em todas as rotas de escrita/remoção.

---

### [HIGH] Ausência total de autenticação e autorização

**File:** Todos os 19 endpoints — `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`

**Description:** Nenhuma rota possui decorator de autenticação. Não há verificação de ownership (IDOR): qualquer um lê/edita tasks de qualquer usuário via `GET /users/<id>/tasks` ou `PUT /tasks/<id>`.

**Impact:** Exposição total de dados, manipulação por qualquer anônimo, escalação horizontal e vertical de privilégios. OWASP A01:2021 (Broken Access Control).

**Recommendation:** Criar `middlewares/auth.py` com `require_auth`/`require_role`, injetar `current_user` no request e validar ownership nos services.

---

### [HIGH] Lógica de negócio dentro das rotas (sem camadas Controller/Service)

**File:** `routes/report_routes.py:12-101` (90 linhas), `routes/task_routes.py:11-63, 85-154, 156-223`, `routes/user_routes.py:42-90`

**Description:** As rotas concentram parsing HTTP, validação, queries, regras de negócio, cálculos de agregação e serialização manual. `summary_report()` sozinha é uma função de 90 linhas com ~20 queries. Não existe camada de controllers nem services (a pasta `services/` contém só um `NotificationService` órfão, nunca importado).

**Impact:** Impossível testar regras de negócio sem subir o Flask; qualquer mudança de regra exige mexer em handlers HTTP; lógica não reutilizável entre endpoints.

**Recommendation:** Extrair para `services/task_service.py`, `user_service.py`, `report_service.py`, `category_service.py`; controllers apenas orquestram HTTP; routes apenas mapeiam URL → controller.

---

### [HIGH] N+1 Query Problem

**File:** `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68, 157-165`

**Description:** Queries executadas dentro de loops:

- `GET /tasks`: para cada task, `User.query.get()` + `Category.query.get()` → **1 + 2N queries** (100 tasks = 201 queries).
- `/reports/summary`: `for u in users: Task.query.filter_by(user_id=u.id).all()` → 1 + N.
- `GET /categories`: `Task.query.filter_by(category_id=c.id).count()` por categoria.

**Impact:** Degradação severa em escala; latência linear no volume de dados; sobrecarga do banco.

**Recommendation:** Usar eager loading (`joinedload(Task.user, Task.category)`) ou agregação com `GROUP BY` em uma única query no repository.

---

### [HIGH] Improper Error Handling (bare except + print)

**File:** `routes/task_routes.py:62, 137, 204, 236`, `routes/user_routes.py:130, 149`, `routes/report_routes.py:186, 207, 221`, `utils/helpers.py:46, 48, 88`

**Description:** Onze ocorrências de `except:` nu (captura `KeyboardInterrupt`/`SystemExit`), exceções silenciadas sem log, e `print()` usado como logging (`task_routes.py:149, 219, 234`, `user_routes.py:83, 89, 147`). `GET /tasks` engole *qualquer* erro num 500 genérico (linhas 62-63).

**Impact:** Bugs impossíveis de diagnosticar em produção; aplicação não desliga graciosamente; ausência de rastreabilidade.

**Recommendation:** Substituir por `except SQLAlchemyError as e` com `logger.error(..., exc_info=True)`; criar `middlewares/error_handler.py` centralizado com `logging` estruturado.

---

### [HIGH] Tight Coupling entre camadas

**File:** `routes/*.py` (todos importam `db`, `Task`, `User`, `Category` diretamente), `services/notification_service.py:15-20`

**Description:** Rotas acessam o ORM e a `db.session` diretamente, sem repositories. `NotificationService` instancia `smtplib.SMTP` internamente, impossibilitando mock.

**Impact:** Nenhuma parte do sistema é testável isoladamente; trocar de ORM ou de provedor de e-mail exige reescrever tudo.

**Recommendation:** Introduzir `repositories/` para acesso a dados e injeção de dependência nos services.

---

### [HIGH] Serialização manual duplicada com divergência de contrato

**File:** `routes/task_routes.py:17-39` vs `models/task.py:23-36` vs `routes/user_routes.py:162-181`

**Description:** A mesma serialização de Task é reimplementada campo a campo em três lugares. `Task.to_dict()` existe mas é ignorado em `GET /tasks`. O campo `overdue` é recalculado em 4 lugares (`task_routes.py:30-39, 71-80`, `user_routes.py:171-180`, `report_routes.py:34-43`) enquanto `Task.is_overdue()` (`models/task.py:50-60`) nunca é chamado.

**Impact:** Contratos de API divergentes entre endpoints; correção de bug precisa ser aplicada em 4 pontos; risco alto de inconsistência.

**Recommendation:** Fonte única de verdade — schema marshmallow para serialização e `Task.is_overdue()` para a regra.

---

### [MEDIUM] Debug mode ativado e bind em 0.0.0.0

**File:** `app.py:34`

**Description:** `app.run(debug=True, host='0.0.0.0', port=5000)` hardcoded. O debug do Werkzeug expõe um console interativo Python.

**Impact:** Se exposto na rede, o debugger permite execução remota de código arbitrário. Stack traces vazam caminhos e estrutura interna.

**Recommendation:** `debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'`, default `False`.

---

### [MEDIUM] CORS totalmente aberto

**File:** `app.py:15`

**Description:** `CORS(app)` sem restrição — `Access-Control-Allow-Origin: *` em todos os endpoints, incluindo os de escrita.

**Impact:** Qualquer site pode chamar a API a partir do browser da vítima.

**Recommendation:** `CORS(app, origins=Config.ALLOWED_ORIGINS)`.

---

### [MEDIUM] Requisitos de senha inseguros

**File:** `routes/user_routes.py:64-65, 115-116`, `seed.py:19, 26, 33`

**Description:** Mínimo de 4 caracteres, sem requisito de complexidade. Seed cria contas com `1234`, `abcd`, `pass` — incluindo um `admin`.

**Impact:** Brute force trivial; conta admin com senha de dicionário.

**Recommendation:** Mínimo de 12 caracteres com validação de complexidade; senhas do seed via variável de ambiente.

---

### [MEDIUM] Validação de input ausente/frágil

**File:** `routes/task_routes.py:113, 182, 261, 264`, `routes/report_routes.py:196-202`

**Description:**

- `priority < 1` compara sem checar tipo → `TypeError` (500) se vier string.
- `int(priority)` / `int(user_id)` em `search_tasks` sem try/except → 500 em `?priority=abc`.
- `update_category` chama `request.get_json()` e acessa `data` sem checar `None` (linha 196) → 500 com body vazio.
- Regex de e-mail (`user_routes.py:61`) aceita `a@b` (sem TLD).
- Nenhum limite de tamanho em `description`/`tags`.

**Impact:** Erros 500 em vez de 400; dados inválidos persistidos; marshmallow está instalado e não é usado.

**Recommendation:** Schemas marshmallow por endpoint em `schemas/`, com `@validates` e tratamento de `ValidationError` → 400.

---

### [MEDIUM] Operações multi-step sem transação explícita

**File:** `routes/user_routes.py:140-151`

**Description:** `delete_user` faz `db.session.delete(t)` num loop **fora** do bloco `try`, e só o `delete(user)` está protegido. Se o loop falhar, a sessão fica suja sem rollback.

**Impact:** Estado inconsistente da sessão; tasks órfãs; comportamento imprevisível na próxima operação.

**Recommendation:** Envolver toda a operação em `try/except` com rollback, ou usar `cascade='all, delete-orphan'` no relacionamento.

---

### [MEDIUM] Ausência de constraints de banco

**File:** `models/task.py:13-14`, `models/category.py:8`

**Description:** FKs `user_id`/`category_id` são `nullable=True` sem `ondelete`; `Category.name` sem `unique`; `Task.status`/`priority` sem CHECK constraint (validação só na aplicação); nenhum índice em `status`, `user_id`, `due_date` — colunas usadas em todos os filtros.

**Impact:** Registros órfãos ao deletar categoria; categorias duplicadas; status inválido gravável por qualquer caminho que não passe pelas rotas; full table scans.

**Recommendation:** Adicionar `unique`, `index=True` nas colunas filtradas e `ondelete='SET NULL'` nas FKs.

---

### [MEDIUM] Dependências divergentes e não utilizadas

**File:** `requirements.txt:4-6`

**Description:** `marshmallow`, `requests` e `python-dotenv` estão declarados mas nunca importados. `PyJWT 2.8.0` está instalado no `.venv` mas **ausente** do `requirements.txt`.

**Impact:** Build reproduzível quebrado; superfície de ataque desnecessária.

**Recommendation:** Sincronizar `requirements.txt` com o uso real após a refatoração.

---

### [LOW] Magic numbers e strings duplicadas

**File:** `routes/task_routes.py:96-114, 167-183`, `routes/user_routes.py:64, 71, 115, 120`, `routes/report_routes.py:24-28, 45, 129`

**Description:** `utils/helpers.py:110-116` **define** `VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`, `MIN_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH` — e nenhuma dessas constantes é importada em lugar nenhum. Os literais `['pending','in_progress','done','cancelled']`, `3`, `200`, `4`, `1..5`, `7` (dias) estão espalhados por 12+ locais.

**Impact:** Alterar o conjunto de status exige editar 6 arquivos; intenção não explícita.

**Recommendation:** Centralizar em `config/constants.py` e importar em todos os pontos de uso.

---

### [LOW] Dead code e imports não utilizados

**File:** `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:7-8`, `utils/helpers.py:3-7`, `services/notification_service.py`

**Description:**

- `import os, sys, json, datetime` — só `datetime` é usado (`app.py:7`).
- `import json, os, sys, time` — nenhum usado (`task_routes.py:7`).
- `import hashlib, json, re` — só `re` usado (`user_routes.py:6`).
- `format_date`/`calculate_percentage` importados em `report_routes.py:7` e nunca chamados.
- `utils/helpers.py`: `os`, `json`, `sys`, `math`, `hashlib` sem uso; `process_task_data`, `generate_id`, `is_valid_color`, `sanitize_string`, `validate_email`, `log_action` nunca chamados.
- `NotificationService` (48 linhas) nunca instanciado em lugar algum do projeto.

**Impact:** Código morto mascara o que realmente está em uso; onboarding mais caro.

**Recommendation:** Remover imports e funções mortos; integrar ou excluir o `NotificationService`.

---

### [LOW] Código verboso / anti-idiomático

**File:** `models/task.py:38-60`, `models/user.py:34-38`, `routes/report_routes.py:119-135`

**Description:** `if cond: return True else: return False` em vez de `return cond` (5 ocorrências); `count = count + 1` em vez de `+=`; `if type(tags) == list` em vez de `isinstance()` (`task_routes.py:141, 210`); `is_overdue()` com 4 níveis de aninhamento.

**Impact:** Legibilidade reduzida; `type() ==` falha com subclasses de `list`.

**Recommendation:** Simplificar para expressões booleanas diretas e usar `isinstance()`.

---

### [LOW] Ausência de documentação e type hints

**File:** Todos os arquivos exceto `seed.py:1`

**Description:** Nenhuma função possui docstring ou type hints. README não documenta os 19 endpoints nem variáveis de ambiente.

**Impact:** Custo alto de onboarding; nenhuma verificação estática possível.

**Recommendation:** Type hints em services/repositories e docstrings nos métodos públicos.

---

### [LOW] Códigos HTTP inadequados

**File:** `routes/task_routes.py:62-63`, `routes/report_routes.py:186-188, 207-209`

**Description:** `GET /tasks` retorna 500 para qualquer falha, inclusive erros de dados. `create_category`/`update_category` retornam 500 em violação de constraint (deveria ser 409/400). `DELETE` retorna 200 com body em vez de 204.

**Impact:** Clientes não conseguem distinguir erro do cliente de erro do servidor; retries incorretos.

**Recommendation:** Mapear `ValidationError`→400, `IntegrityError`→409, ausência→404 no error handler centralizado.

---

## Conclusão

**Total: 23 findings** (5 CRITICAL, 6 HIGH, 7 MEDIUM, 5 LOW)

**Risco agregado:** a combinação de MD5 sem salt + campo `password` exposto no `to_dict()` + token de autenticação falso + endpoints `DELETE` públicos significa que **a base inteira pode ser lida, alterada e apagada por qualquer requisição anônima**, e as senhas de todos os usuários podem ser recuperadas offline a partir de um único `GET /users/1`.

**Prioridade de correção:**

1. **Bloqueia deploy** — os 5 CRITICAL (crypto, vazamento de hash, secrets, token falso, DELETE público)
2. **Antes de produção** — os 6 HIGH (auth, separação de camadas, N+1, error handling, coupling, duplicação)
3. **Technical debt** — os 7 MEDIUM
4. **Melhoria contínua** — os 5 LOW
