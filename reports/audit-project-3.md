# Architecture Audit Report - Project 3

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   11 analyzed | ~600 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 2 | LOW: 1

Total: 11 findings

---

## Findings

### [CRITICAL] Hardcoded Secret Key in Source Code

File: app.py:13

Description: Flask SECRET_KEY hardcoded como placeholder fraco. Commitado em controle de versão e exposto a qualquer pessoa com acesso ao repositório.

Code:
```python
app.config['SECRET_KEY'] = 'super-secret-key-123'
```

Impact: Tokens de sessão podem ser forjados por atacantes. Tokens CSRF podem ser bypassados. Validação JWT completamente comprometida. Qualquer pessoa com acesso ao código pode personificar qualquer usuário.

Recommendation: Carregar de variáveis de ambiente usando `os.getenv('SECRET_KEY')` ou arquivos de config. Gerar chaves fortes aleatórias (mínimo 32 bytes). Nunca commitar secrets em git.

---

### [CRITICAL] Hardcoded Email Credentials in Source Code

File: services/notification_service.py:9-10

Description: Credenciais SMTP hardcoded diretamente na classe. Senha fraca ("senha123"). Source-controlled e visível para todos.

Code:
```python
self.email_user = 'taskmanager@gmail.com'
self.email_password = 'senha123'
```

Impact: Atacante pode enviar emails personificando a aplicação. Conta de email pode ser sequestrada. Potencial para ataques baseados em email e spam. Violação de políticas de segurança cloud.

Recommendation: Usar variáveis de ambiente, serviço de secrets management (AWS Secrets Manager, HashiCorp Vault), ou arquivos de config excluídos do git. Usar `.env` com `python-dotenv` (já em requirements.txt mas não usado).

---

### [CRITICAL] Weak Password Hashing with MD5

File: models/user.py:27-32

Description: MD5 usado para hash de senhas. MD5 está criptograficamente quebrado - é rápido (ruim para senhas) e tem colisões conhecidas. Sem salt. Trivial crackear com rainbow tables.

Code:
```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

Impact: Senhas podem ser crackeadas em minutos mesmo se banco for roubado. Rainbow tables com hashes MD5 pré-computados existem online. Todas as contas de usuário comprometidas se banco vazar. Não-compliant com padrões de segurança (OWASP, PCI-DSS).

Recommendation: Usar `bcrypt`, `argon2`, ou `scrypt`. Flask-Bcrypt é escolha padrão. Mínimo 12 rounds para bcrypt. Usar `werkzeug.security.generate_password_hash` e `check_password_hash`.

---

### [CRITICAL] Plaintext Password Exposed in User API Response

File: models/user.py:16-25

Description: Hash de senha de usuário incluído em toda resposta de API (GET /users, GET /users/<id>, login). Mesmo sendo hash, nunca deve ser exposto.

Code:
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,  # Hash exposto!
        'role': self.role,
        'active': self.active,
        'created_at': str(self.created_at)
    }
```

Impact: Hashes de senha vazados para todos os consumidores de API. Habilita ataques de cracking offline. Frontend/logs/ferramentas de monitoramento inadvertidamente armazenam dados sensíveis. Violação de compliance (PCI-DSS, GDPR).

Recommendation: Remover 'password' do método `to_dict()`. Criar métodos separados para diferentes contextos com `include_password=False` por padrão.

---

### [HIGH] No Authentication/Authorization on Any Endpoint

File: All routes (task_routes.py, user_routes.py, report_routes.py)

Description: Todos os endpoints são publicamente acessíveis. Sem validação JWT, sem checking de role, sem middleware de autenticação. Endpoint de login existe mas token nunca é validado.

Code Evidence:
```python
# user_routes.py:210
'token': 'fake-jwt-token-' + str(user.id)  # Token fake, nunca validado!
```

Impact: Usuários não autenticados podem acessar todos os dados. Usuários podem modificar dados de outros usuários (IDOR). User A pode deletar tasks de User B sem permissão. Bypass completo de autorização.

Recommendation: Implementar middleware de autenticação baseado em decorator. Usar Flask-JWT-Extended ou similar. Checar token em todo endpoint. Implementar controle de acesso baseado em role (RBAC). Prevenir IDOR: verificar que usuário possui recurso antes de modificação.

---

### [HIGH] Improper Error Handling with Generic Messages but Detailed Logging

File: routes/task_routes.py:62-63, 149-154

Description: Bare `except:` captura TODAS as exceções silenciosamente. Logging via print ao invés de framework de logging apropriado. Formato de error response inconsistente.

Code:
```python
try:
    # ... lógica de negócio
except:  # Captura até KeyboardInterrupt!
    return jsonify({'error': 'Erro interno'}), 500

except Exception as e:
    db.session.rollback()
    print(f"Task criada: {task.id}")  # Print ao invés de logger
    return jsonify({'error': 'Erro ao criar task'}), 500
```

Impact: Erros falham silenciosamente sem capacidade de investigação. Sem stack traces para debug. Disclosure de informação (pode vazar detalhes em alguns casos). Logs de produção poluídos com print statements.

Recommendation: Usar módulo `logging` do Python. Capturar exceções específicas. Logar tracebacks completos para debugging. Retornar mensagens user-friendly mas logar erros. Configurar error handlers apropriados.

---

### [HIGH] Business Logic in Route Handlers (Tight Coupling)

File: task_routes.py:11-63, report_routes.py:12-101

Description: Cálculo de overdue duplicado 4+ vezes. Serialização manual. Queries em routes. Sem uso de service layer apesar de pasta `services/` existir.

Code Example:
```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  # Query em route
    for t in tasks:
        task_data = {}  # Serialização manual
        # ... 10+ atribuições de campo
        if t.due_date:  # Lógica de negócio (overdue)
            if t.due_date < datetime.utcnow():
                if t.status != 'done' and t.status != 'cancelled':
                    task_data['overdue'] = True
```

Impact: Viola single responsibility principle. Impossível testar lógica sem camada HTTP. Código duplicado. Não pode reutilizar lógica em outros contextos.

Recommendation: Extrair para TaskService. Mover cálculo de overdue para Task model ou método de service. Usar marshmallow para serialização. Criar service layer para qual routes delegam.

---

### [HIGH] Bare Except Clause Catching All Exceptions

File: user_routes.py:130, task_routes.py:62, report_routes.py:187, 207, 223

Description: `except:` sem tipo de exceção captura SystemExit, KeyboardInterrupt e outras exceções não-recuperáveis.

Impact: Debug extremamente difícil. Mascara erros críticos de sistema. Difícil distinguir entre erros de banco e outros problemas. Aplicação pode não desligar cleanly.

Recommendation: Ser específico: `except (IntegrityError, DataError, SQLAlchemyError) as e:`. Logar exceções com stack trace. Diferenciar entre erros esperados e inesperados.

---

### [MEDIUM] Insecure Password Requirements

File: routes/user_routes.py:64-65, utils/helpers.py:114

Description: Senha mínima de apenas 4 caracteres. Sem requisitos de complexidade. Seed data usa senhas fracas.

Code:
```python
if len(password) < 4:
    return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400

# seed.py:19, 26, 33
u1.set_password('1234')
u2.set_password('abcd')
u3.set_password('pass')
```

Impact: Ataques de força bruta triviais. Ataques de dicionário bem-sucedidos. Credenciais seed em produção comprometem todas as contas. Não-compliant com guidelines NIST/OWASP.

Recommendation: Mínimo 12 caracteres. Requerer mix de uppercase/lowercase/números/caracteres especiais. Usar password strength meter. Remover credenciais fracas de seed data. Seguir NIST guidelines: https://pages.nist.gov/800-63-3/sp800-63b.html

---

### [MEDIUM] Vulnerable Search Endpoint (LIKE Injection)

File: routes/task_routes.py:240-271

Description: LIKE operator sem sanitização de caracteres especiais. Sem rate limiting em search.

Code:
```python
query = request.args.get('q', '')
tasks = tasks.filter(
    db.or_(
        Task.title.like(f'%{query}%'),
        Task.description.like(f'%{query}%')
    )
)
```

Impact: Usuário pode usar `%` para wildcards além da intenção. Information disclosure através de pattern matching. Degradação de performance (LIKE em colunas sem índice). Sem rate limiting.

Recommendation: Escapar caracteres especiais LIKE: `query.replace('%', '\\%').replace('_', '\\_')`. Considerar alternativas de full-text search. Adicionar rate limiting ao endpoint de search. Implementar paginação de resultados de query. Adicionar audit logging de search.

---

### [LOW] Magic Numbers and Constants Not Centralized

File: Scattered throughout routes and models

Description: Range de prioridade (`1` e `5`), valores de status (`['pending', 'in_progress', 'done', 'cancelled']`), separador de tags (`','`), formato de data (`'%Y-%m-%d'`) duplicados.

Examples:
- `task_routes.py:110`: `if status not in ['pending', 'in_progress', 'done', 'cancelled']`
- `task_routes.py:113`: `if priority < 1 or priority > 5`
- `helpers.py:110-115`: Constantes definidas mas não usadas em todo lugar
- `models/task.py:39`: Mesma lista de status hardcoded novamente

Impact: Mudanças requerem atualizar múltiplos arquivos. Risco de inconsistência. Menos legível.

Recommendation: Consolidar em `constants.py` ou `config.py`. Importar e usar consistentemente em toda aplicação.

---

================================
Total: 11 findings
================================

## Refactoring Impact

After implementing the recommended fixes:

**Security**:
- ✅ Strong SECRET_KEY from environment
- ✅ Email credentials secured
- ✅ Passwords hashed with bcrypt (not MD5)
- ✅ No password exposure in API responses
- ✅ JWT authentication implemented
- ✅ Strong password requirements (12+ chars)

**Architecture**:
- ✅ Business logic extracted to services
- ✅ Proper use of service layer
- ✅ Clean separation of concerns
- ✅ Reusable, testable code

**Reliability**:
- ✅ Proper error handling
- ✅ Structured logging (not print statements)
- ✅ Specific exception catching
- ✅ Consistent error responses

**Maintainability**:
- ✅ Constants centralized
- ✅ No code duplication
- ✅ Clean, readable code
- ✅ Production-ready
