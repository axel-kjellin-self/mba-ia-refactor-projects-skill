# Catálogo de Anti-Patterns

Este catálogo lista anti-patterns comuns em projetos legados, com sinais de detecção e classificação de severidade.

---

## CRITICAL SEVERITY

### 1. SQL Injection

**Descrição**: Queries SQL construídas com concatenação de strings ao invés de queries parametrizadas.

**Sinais de Detecção**:
- Python: `cursor.execute("SELECT * FROM table WHERE id = " + str(id))`
- Python: `cursor.execute(f"SELECT * FROM table WHERE id = {id}")`
- Python: String concatenation com `+` dentro de `execute()`
- JavaScript/Node: `db.query("SELECT * FROM table WHERE id = " + id)`
- JavaScript/Node: Template literals em queries: `` db.query(`SELECT ... WHERE id = ${id}`) ``
- Qualquer linguagem: Queries construídas com concatenação de strings

**Impacto**: Comprometimento completo do banco de dados, roubo de dados, modificação/exclusão de dados, acesso não autorizado.

**Severidade**: CRITICAL

---

### 2. Hardcoded Credentials

**Descrição**: Credenciais, secrets e senhas hardcoded no código-fonte.

**Sinais de Detecção**:
- Patterns regex:
  - `SECRET_KEY = "..."`
  - `password = "..."`
  - `dbPass: "..."`
  - `API_KEY = "..."`
  - Strings contendo "password", "secret", "key", "token" atribuídas a valores literais
- Python: `app.config['SECRET_KEY'] = 'hardcoded-value'`
- JavaScript: `const password = 'hardcoded-value'`
- Senhas em dicionários/objetos de configuração
- Credenciais em seed data ou fixtures

**Impacto**: Comprometimento de sistemas, acesso não autorizado, violação de compliance (PCI-DSS, SOC2).

**Severidade**: CRITICAL

---

### 3. Weak Cryptography / Broken Password Hashing

**Descrição**: Uso de algoritmos criptográficos quebrados ou fracos para hash de senhas.

**Sinais de Detecção**:
- Python: `hashlib.md5()`, `hashlib.sha1()` para senhas
- Python: `base64.b64encode()` para "hash" de senhas
- JavaScript: `crypto.createHash('md5')` para senhas
- Qualquer uso de MD5, SHA1, ou base64 para armazenar senhas
- Funções de hash customizadas/caseiras
- Hash sem salt

**Algoritmos Quebrados**:
- MD5 (quebrado desde 2004)
- SHA1 (quebrado desde 2017)
- Base64 (encoding, não hash)

**Impacto**: Senhas crackeadas em minutos/horas, comprometimento de todas as contas em caso de breach.

**Severidade**: CRITICAL

**Nota**: Algoritmos seguros incluem bcrypt, argon2, scrypt, PBKDF2.

---

### 4. Plaintext Password Storage

**Descrição**: Senhas armazenadas em texto plano sem qualquer hash.

**Sinais de Detecção**:
- Comparação direta de senhas: `if password == stored_password:`
- SQL INSERT com senhas literais: `INSERT INTO users (..., password) VALUES (..., 'senha123')`
- Senhas em seed data sem hash
- Ausência de função de hash antes de salvar senha

**Impacto**: Qualquer breach do banco expõe todas as senhas dos usuários.

**Severidade**: CRITICAL

---

### 5. Exposed Secrets in API Responses

**Descrição**: Secrets, hashes de senha ou informações sensíveis expostas em respostas de API.

**Sinais de Detecção**:
- Python: `to_dict()` ou serializadores incluindo campo `password`
- JavaScript: JSON responses incluindo `password`, `secret_key`, `api_key`
- Endpoints de health check retornando configurações sensíveis
- Debug endpoints expondo variáveis de ambiente

**Impacto**: Vazamento de credenciais, permite ataques offline de cracking, violação de compliance.

**Severidade**: CRITICAL

---

### 6. Unrestricted Dangerous Endpoints

**Descrição**: Endpoints destrutivos ou administrativos sem autenticação/autorização.

**Sinais de Detecção**:
- Endpoints como `/admin/reset-db`, `/admin/query`, `/debug`
- DELETE ou modificação de dados sem verificação de permissões
- Rotas de admin sem decorators de autenticação
- Execução de queries arbitrárias via API

**Impacto**: Perda de dados, denial of service, comprometimento completo do sistema.

**Severidade**: CRITICAL

---

## HIGH SEVERITY

### 7. Missing Authentication/Authorization

**Descrição**: Endpoints acessíveis sem autenticação ou verificação de autorização.

**Sinais de Detecção**:
- Python/Flask: Rotas sem decorators `@login_required` ou `@jwt_required`
- JavaScript/Express: Rotas sem middleware de autenticação
- Login endpoint que não gera token ou sessão
- Ausência de verificação de ownership (IDOR vulnerability)
- Tokens fake ou não validados: `'fake-jwt-token-' + id`

**Impacto**: Acesso não autorizado, manipulação de dados por usuários não privilegiados, escalação de privilégios.

**Severidade**: HIGH

---

### 8. God Class / God Method

**Descrição**: Classe ou arquivo único contendo múltiplas responsabilidades (dados, lógica, apresentação).

**Sinais de Detecção**:
- Arquivos com 200+ linhas contendo múltiplos domínios
- Classes com 10+ métodos públicos de responsabilidades diferentes
- Arquivo/classe que contém:
  - Acesso a banco de dados
  - Validação
  - Lógica de negócio
  - Formatação/serialização
  - Múltiplos domínios (users, products, orders no mesmo lugar)

**Impacto**: Código impossível de testar em isolamento, difícil manutenção, alto acoplamento.

**Severidade**: HIGH

---

### 9. N+1 Query Problem

**Descrição**: Queries executadas dentro de loops, causando explosão de acesso ao banco.

**Sinais de Detecção**:
- Loop `for`/`forEach` contendo queries de banco dentro
- Python: `for item in items:` seguido de `cursor.execute()` ou `Model.query.get()`
- JavaScript: `items.forEach(item => { db.query(...) })`
- Queries aninhadas: loop dentro de loop com queries
- Ausência de JOINs quando há relações entre tabelas

**Análise**: Para N itens, executa 1 + N queries ao invés de 1 query com JOIN.

**Impacto**: Degradação severa de performance, sobrecarga do banco de dados.

**Severidade**: HIGH

---

### 10. Business Logic in Controllers/Routes

**Descrição**: Lógica de negócio implementada diretamente em route handlers ao invés de service layer.

**Sinais de Detecção**:
- Cálculos complexos dentro de funções de rota
- Validação de regras de negócio em controllers
- Queries de banco direto em route handlers
- Serialização manual campo-por-campo em routes
- Lógica duplicada em múltiplas rotas

**Exemplos**:
- Cálculo de desconto em route handler
- Validação de estoque em endpoint
- Cálculo de overdue/vencimento em GET routes

**Impacto**: Impossível testar lógica sem framework HTTP, código duplicado, não reutilizável.

**Severidade**: HIGH

---

### 11. Callback Hell (JavaScript/Node.js)

**Descrição**: Callbacks profundamente aninhados, criando código ilegível e difícil de manter.

**Sinais de Detecção**:
- 5+ níveis de aninhamento de callbacks
- Padrão pyramid of doom (código vai para direita)
- Callbacks dentro de callbacks dentro de callbacks
- Tratamento de erro duplicado em cada nível

**Impacto**: Código não manutenível, bugs difíceis de rastrear, tratamento de erro inconsistente.

**Severidade**: HIGH

**Nota**: Solução moderna é async/await ou Promises.

---

### 12. Tight Coupling Between Layers

**Descrição**: Dependências diretas entre camadas sem abstração ou injeção de dependência.

**Sinais de Detecção**:
- Controllers importando e chamando models diretamente
- Models contendo lógica de apresentação
- Ausência de interfaces ou abstrações
- Imports diretos de módulos específicos ao invés de interfaces
- Impossível substituir implementação para testes (mocking)

**Impacto**: Impossível testar com mocks, não pode trocar implementações, alto acoplamento.

**Severidade**: HIGH

---

### 13. Improper Error Handling

**Descrição**: Tratamento de erro inadequado, bare except, ou logging incorreto.

**Sinais de Detecção**:
- Python: `except:` sem tipo de exceção (bare except)
- Python: Captura de `Exception` genérico sem logging
- JavaScript: `catch(e) {}` vazio
- Uso de `print()` ou `console.log()` ao invés de logger
- Exceções silenciadas sem ação
- Retorno de 500 para erros de validação (deveria ser 400)

**Impacto**: Bugs impossíveis de debugar, informação perdida, aplicação não desliga gracefully.

**Severidade**: HIGH

---

## MEDIUM SEVERITY

### 14. Code Duplication

**Descrição**: Lógica duplicada em múltiplos lugares.

**Sinais de Detecção**:
- Blocos de código idênticos ou muito similares (10+ linhas)
- Mesma transformação de dados repetida 3+ vezes
- Serialização manual repetida
- Validações duplicadas

**Impacto**: Mudanças requerem atualizar múltiplos lugares, inconsistências, mais bugs.

**Severidade**: MEDIUM

---

### 15. Missing Input Validation

**Descrição**: Endpoints que não validam inputs adequadamente.

**Sinais de Detecção**:
- Acesso direto a `request.body` ou `request.args` sem validação
- Ausência de validação de tipo
- Sem validação de range (números negativos, valores fora de limites)
- Sem validação de formato (email, URL, data)
- Foreign keys não verificadas antes de uso
- Conversões de tipo silenciosas sem try-catch

**Impacto**: Dados inválidos no banco, crashes, security bypasses.

**Severidade**: MEDIUM

---

### 16. Race Conditions / Missing Transactions

**Descrição**: Operações multi-step sem transações, causando possível inconsistência.

**Sinais de Detecção**:
- Múltiplos INSERTs/UPDATEs sem `BEGIN TRANSACTION`
- Python SQLAlchemy: Múltiplas operações sem `db.session` transaction
- Operações dependentes sem rollback em caso de falha
- Checkout/pagamento sem transaction

**Impacto**: Dados inconsistentes, registros órfãos, perda de integridade.

**Severidade**: MEDIUM

---

### 17. Missing Database Constraints

**Descrição**: Ausência de foreign keys, constraints, ou indexes.

**Sinais de Detecção**:
- CREATE TABLE sem FOREIGN KEY constraints
- Relações entre tabelas sem constraints
- Ausência de UNIQUE constraints onde apropriado
- Sem NOT NULL em campos obrigatórios

**Impacto**: Registros órfãos, integridade referencial violada.

**Severidade**: MEDIUM

---

### 18. Debug Mode Enabled in Production

**Descrição**: Debug mode ou verbose logging habilitado em produção.

**Sinais de Detecção**:
- Python/Flask: `app.config['DEBUG'] = True` hardcoded
- JavaScript: `NODE_ENV` não configurado
- Stack traces completos em responses de erro
- Debugger interativo acessível

**Impacto**: Informações sensíveis expostas, debugger permite execução de código.

**Severidade**: MEDIUM

---

### 19. Insecure Password Requirements

**Descrição**: Requisitos de senha muito fracos.

**Sinais de Detecção**:
- Mínimo de senha < 8 caracteres (idealmente 12+)
- Sem requisitos de complexidade
- Senhas triviais em seed data: "1234", "password", "admin"
- Validação apenas de comprimento, sem outros requisitos

**Impacto**: Ataques de brute force, ataques de dicionário bem-sucedidos.

**Severidade**: MEDIUM

---

### 20. Deprecated API Usage

**Descrição**: Uso de APIs ou bibliotecas deprecadas.

**Sinais de Detecção**:
- Python 2.x syntax em código novo
- Flask: `flask.ext.*` (deprecado)
- JavaScript: `var` ao invés de `let`/`const`
- Node.js: callbacks ao invés de Promises/async-await
- Bibliotecas com vulnerabilidades conhecidas (verificar package.json/requirements.txt)

**Impacto**: Vulnerabilidades de segurança, código não manutenível, difícil upgrade.

**Severidade**: MEDIUM

---

### 21. LIKE Injection / Query Performance Issues

**Descrição**: Uso inseguro de LIKE operator ou queries não otimizadas.

**Sinais de Detecção**:
- LIKE com input de usuário sem escape: `.like(f'%{user_input}%')`
- LIKE em colunas sem índice
- Queries complexas sem LIMIT/pagination
- Full table scans

**Impacto**: Information disclosure, degradação de performance.

**Severidade**: MEDIUM

---

## LOW SEVERITY

### 22. Magic Numbers

**Descrição**: Números e strings hardcoded sem constantes nomeadas.

**Sinais de Detecção**:
- Números literais em lógica de negócio: `if price > 1000:`, `discount = 0.1`
- Strings duplicadas: status values, error messages
- Thresholds e limites hardcoded
- Constantes definidas mas não usadas consistentemente

**Impacto**: Difícil manutenção, intenção do código não clara.

**Severidade**: LOW

---

### 23. Poor Variable Naming

**Descrição**: Nomes de variáveis não descritivos ou confusos.

**Sinais de Detecção**:
- Variáveis de uma letra: `x`, `y`, `i` (fora de loops simples)
- Nomes genéricos: `data`, `info`, `temp`, `result`
- Abreviações não óbvias: `usr`, `pwd`, `msg`
- Nomes que não descrevem propósito

**Impacto**: Código difícil de ler e entender.

**Severidade**: LOW

---

### 24. Missing Documentation

**Descrição**: Ausência de docstrings, type hints, ou comentários.

**Sinais de Detecção**:
- Funções sem docstrings
- Python: Sem type hints
- JavaScript: Sem JSDoc
- Lógica complexa sem comentários explicativos
- README sem instruções de setup

**Impacto**: Alto custo de onboarding, código difícil de usar corretamente.

**Severidade**: LOW

---

### 25. Unused Code / Dead Code

**Descrição**: Imports, variáveis, ou funções não utilizadas.

**Sinais de Detecção**:
- Imports que não são referenciados
- Funções definidas mas nunca chamadas
- Variáveis atribuídas mas não lidas
- Código comentado por longos períodos

**Impacto**: Confusão, código inchado, difícil manutenção.

**Severidade**: LOW

---

### 26. Inadequate HTTP Status Codes

**Descrição**: Uso incorreto de códigos HTTP de resposta.

**Sinais de Detecção**:
- Retornar 500 para erros de validação (deveria ser 400)
- Retornar 200 para operações que falharam
- Não usar 404 para recurso não encontrado
- Não usar 401/403 para erros de autenticação/autorização

**Impacto**: Clientes de API não conseguem distinguir tipos de erro.

**Severidade**: LOW

---

## Resumo de Severidades

| Severidade | Exemplos | Prioridade |
|------------|----------|------------|
| CRITICAL (6) | SQL Injection, Hardcoded Secrets, Weak Crypto, Plaintext Passwords, Exposed Secrets, Dangerous Endpoints | Bloqueia deploy |
| HIGH (7) | Missing Auth, God Class, N+1 Queries, Business Logic in Routes, Callback Hell, Tight Coupling, Poor Error Handling | Fix antes de produção |
| MEDIUM (8) | Code Duplication, Missing Validation, Race Conditions, Missing Constraints, Debug Mode, Weak Passwords, Deprecated APIs, LIKE Injection | Technical debt |
| LOW (4) | Magic Numbers, Poor Naming, Missing Docs, Dead Code | Melhoria contínua |

**Total**: 25 anti-patterns catalogados
