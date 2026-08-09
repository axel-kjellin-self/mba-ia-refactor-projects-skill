# Análise Manual dos Projetos - MBA IA Refactor Challenge

## Resumo Executivo

Esta análise documenta os problemas arquiteturais, de segurança e qualidade de código encontrados nos 3 projetos legados. Os achados servirão como base para a criação da skill `/refactor-arch`.

### Estatísticas Gerais

| Projeto | Stack | Arquitetura Atual | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|-------|-------------------|----------|------|--------|-----|-------|
| code-smells-project | Python/Flask | Monolítica (4 arquivos) | 5 | 5 | 6 | 4 | 20 |
| ecommerce-api-legacy | Node.js/Express | Monolítica (3 arquivos) | 5 | 4 | 3 | 3 | 15 |
| task-manager-api | Python/Flask | Semi-organizada (camadas) | 4 | 4 | 2 | 1 | 11 |
| **TOTAL** | - | - | **14** | **13** | **11** | **8** | **46** |

---

## Projeto 1: code-smells-project (Python/Flask E-commerce API)

### Contexto
- **Stack**: Python 3.x + Flask 3.1.1
- **Domínio**: API de E-commerce (produtos, pedidos, usuários)
- **Arquitetura**: Monolítica - tudo em 4 arquivos sem separação de camadas
- **Arquivos**: app.py, controllers.py, models.py, database.py
- **Linhas de código**: ~800 LOC

---

### CRITICAL - Problemas Críticos (5)

#### 1.1 SQL Injection em Múltiplos Endpoints
- **Severidade**: CRITICAL
- **Arquivos**: `models.py` (linhas 28, 48-49, 57-60, 68, 92, 109-110, 127-128, 140, 148-150, etc.), `app.py` (linhas 59-69)
- **Descrição**: Queries SQL construídas com concatenação de strings ao invés de queries parametrizadas
- **Exemplo**:
  ```python
  # models.py:28
  cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

  # models.py:109-110 - Bypass de login
  cursor.execute(
      "SELECT * FROM usuarios WHERE email = '" + email +
      "' AND senha = '" + senha + "'"
  )

  # app.py:59-69 - Endpoint de query arbitrária
  query = dados.get("sql", "")
  cursor.execute(query)
  ```
- **Impacto**: Comprometimento completo do banco de dados, roubo de dados, modificação/exclusão de dados, acesso não autorizado
- **Vetores de Ataque**:
  - `' OR '1'='1` - extrair todos os dados
  - `admin' --` - bypass de login
  - `'; DROP TABLE usuarios; --` - destruição de dados
- **Recomendação**: Usar queries parametrizadas com `?` placeholders ou migrar para SQLAlchemy ORM

#### 1.2 Credenciais Hardcoded no Código
- **Severidade**: CRITICAL
- **Arquivos**: `app.py` (linhas 7, 289), `database.py` (linhas 76-78)
- **Descrição**: Secrets e credenciais em texto puro no código-fonte
- **Exemplo**:
  ```python
  # app.py:7
  app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"

  # database.py:76-78
  usuarios = [
      ("Admin", "admin@loja.com", "admin123", "admin"),
      ("João Silva", "joao@email.com", "123456", "cliente"),
  ]

  # controllers.py:289 - Exposto em health_check
  "secret_key": "minha-chave-super-secreta-123"
  ```
- **Impacto**:
  - SECRET_KEY comprometida permite forjar sessões/JWT
  - Credenciais padrão permitem acesso não autorizado
  - Segredos expostos em respostas de API
- **Recomendação**: Usar variáveis de ambiente (python-dotenv), nunca commitar credenciais, nunca expor secrets em APIs

#### 1.3 Endpoint de Reset de Banco sem Autenticação
- **Severidade**: CRITICAL
- **Arquivo**: `app.py` (linhas 47-57)
- **Descrição**: `/admin/reset-db` pode ser invocado por qualquer usuário para destruir todos os dados
- **Exemplo**:
  ```python
  @app.route("/admin/reset-db", methods=["POST"])
  def reset_database():
      # Sem nenhuma autenticação!
      cursor.execute("DELETE FROM itens_pedido")
      cursor.execute("DELETE FROM pedidos")
      cursor.execute("DELETE FROM produtos")
      cursor.execute("DELETE FROM usuarios")
  ```
- **Impacto**: Perda completa de dados, denial of service, interrupção de negócio
- **Recomendação**: Implementar autenticação/autorização, requerer role admin, adicionar confirmação, remover em produção

#### 1.4 Endpoint de Query Arbitrária sem Restrições
- **Severidade**: CRITICAL
- **Arquivo**: `app.py` (linhas 59-78)
- **Descrição**: `/admin/query` aceita SQL arbitrário do request body
- **Exemplo**:
  ```python
  @app.route("/admin/query", methods=["POST"])
  def executar_query():
      query = dados.get("sql", "")
      cursor.execute(query)  # Executa qualquer SQL!
  ```
- **Impacto**: Acesso completo ao banco, execução arbitrária de queries, roubo/manipulação de dados
- **Recomendação**: Remover endpoint completamente ou implementar controle de acesso rigoroso

#### 1.5 Senhas em Texto Plano
- **Severidade**: CRITICAL
- **Arquivos**: `database.py` (linhas 76-78), `models.py` (linhas 105-120, 122-131)
- **Descrição**: Senhas armazenadas sem hash, comparação direta de texto
- **Exemplo**:
  ```python
  # database.py
  usuarios = [("Admin", "admin@loja.com", "admin123", "admin")]

  # models.py:109-110
  cursor.execute(
      "SELECT * FROM usuarios WHERE email = '" + email +
      "' AND senha = '" + senha + "'"
  )
  ```
- **Impacto**: Qualquer breach do banco expõe todas as senhas, senhas visíveis em logs
- **Recomendação**: Usar bcrypt ou Argon2 para hash de senhas

---

### HIGH - Problemas Graves (5)

#### 1.6 Ausência de Autenticação/Autorização
- **Severidade**: HIGH
- **Arquivo**: `app.py` (todas as rotas)
- **Descrição**: Nenhum endpoint exige autenticação. Endpoint de login não gera tokens
- **Impacto**: Acesso não autorizado a todas as funcionalidades, manipulação de dados por usuários não privilegiados
- **Recomendação**: Implementar JWT ou Flask-Login, criar decorators de autorização, implementar RBAC

#### 1.7 God Class em models.py
- **Severidade**: HIGH
- **Arquivo**: `models.py` (todo o arquivo, 315 linhas)
- **Descrição**: Um único arquivo contém 15+ funções misturando acesso a dados, validação e lógica de negócio
- **Funções**: get_todos_produtos, get_usuario_por_id, criar_pedido (com gestão de inventário), relatorio_vendas
- **Exemplo**:
  ```python
  def criar_pedido(usuario_id, itens):
      # Acesso a dados + lógica de negócio + validação
      total = 0
      for item in itens:
          cursor.execute("SELECT * FROM produtos WHERE id = ...")
          if produto["estoque"] < item["quantidade"]:
              return {"erro": "Estoque insuficiente"}
          total = total + (produto["preco"] * item["quantidade"])
      cursor.execute("INSERT INTO pedidos ...")
  ```
- **Impacto**: Difícil testar (precisa de BD), impossível reutilizar lógica, acoplamento forte com banco
- **Recomendação**: Separar em camadas: Repository/DAL, Service, Controller. Usar injeção de dependência

#### 1.8 Problema N+1 de Queries
- **Severidade**: HIGH
- **Arquivo**: `models.py` (linhas 171-201, 203-233)
- **Descrição**: `get_pedidos_usuario()` e `get_todos_pedidos()` criam múltiplas queries em loops aninhados
- **Exemplo**:
  ```python
  for row in rows:  # 1 query inicial
      cursor2 = db.cursor()
      cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ...")  # N queries
      for item in itens:
          cursor3 = db.cursor()
          cursor3.execute("SELECT nome FROM produtos WHERE id = ...")  # N*M queries
  ```
- **Análise**: Para 10 pedidos: 1 + 10 + 20 = 31 queries (deveria ser 3 com JOINs)
- **Impacto**: Degradação severa de performance em escala, sobrecarga no BD, respostas lentas
- **Recomendação**: Usar SQL JOINs, paginação, caching, migrar para ORM (SQLAlchemy)

#### 1.9 Armazenamento de Senhas em Texto Plano
- **Severidade**: HIGH
- **Arquivos**: `database.py`, `models.py`
- **Descrição**: Senhas armazenadas e comparadas sem hash
- **Impacto**: Breach do banco expõe todas as senhas, sem proteção contra reuso de senhas
- **Recomendação**: bcrypt, Argon2, nunca armazenar texto plano

#### 1.10 Validação de Input Incompleta
- **Severidade**: HIGH
- **Arquivo**: `controllers.py`
- **Descrição**: Múltiplos endpoints com validação ausente ou incompleta
- **Exemplos**:
  - `criar_pedido()` (195-201): não valida se usuario_id existe
  - `buscar_usuario()` (136-144): não valida se ID é inteiro positivo
  - `buscar_produtos()` (113-116): não valida preços negativos
  - `criar_usuario()` (154-155): não valida formato de email
- **Impacto**: Dados inválidos no banco, erros em cálculos, bypasses de segurança
- **Recomendação**: Usar biblioteca de validação (marshmallow, pydantic), validação centralizada, sanitizar todos os inputs

---

### MEDIUM - Problemas Moderados (6)

#### 1.11 Duplicação de Código em Transformações
- **Severidade**: MEDIUM
- **Arquivo**: `models.py` (linhas 10-21, 78-86, 95-102, 178-200, 211-231)
- **Descrição**: Lógica de transformação produto/pedido repetida 5+ vezes
- **Impacto**: Pesadelo de manutenção, transformações inconsistentes, código inchado
- **Recomendação**: Criar classes serializadoras, usar dataclasses, centralizar transformações

#### 1.12 Acoplamento Forte Entre Camadas
- **Severidade**: MEDIUM
- **Arquivos**: `controllers.py`, `models.py`
- **Descrição**: Controllers chamam models diretamente que chamam banco diretamente. Sem abstração, sem injeção de dependência
- **Impacto**: Impossível mockar banco para testes, não pode trocar BD sem reescrever tudo
- **Recomendação**: Implementar Repository pattern, usar injeção de dependência, criar service layer

#### 1.13 Debug Mode Ativado em Produção
- **Severidade**: MEDIUM
- **Arquivo**: `app.py` (linha 8)
- **Descrição**: `app.config["DEBUG"] = True` hardcoded
- **Impacto**: Debugger interativo que pode executar código, stack traces com informações sensíveis
- **Recomendação**: Carregar de variável de ambiente, desabilitar em produção

#### 1.14 Tratamento de Erros Inconsistente
- **Severidade**: MEDIUM
- **Arquivo**: `models.py` (linhas 133-169)
- **Descrição**: `criar_pedido()` retorna dicionários de erro misturados com sucesso
- **Impacto**: Respostas de API inconsistentes, tratamento de erro difícil em controllers
- **Recomendação**: Sempre lançar exceções para erros, usar try-catch em controllers

#### 1.15 Magic Numbers Sem Constantes
- **Severidade**: MEDIUM
- **Arquivo**: `models.py` (linhas 256-262)
- **Descrição**: Cálculo de desconto usa thresholds e percentuais hardcoded
- **Exemplo**:
  ```python
  desconto = 0
  if faturamento > 10000:
      desconto = faturamento * 0.1
  elif faturamento > 5000:
      desconto = faturamento * 0.05
  ```
- **Impacto**: Lógica de negócio não manutenível, difícil testar edge cases
- **Recomendação**: Extrair para arquivo de config ou constantes

#### 1.16 Documentação e Type Hints Ausentes
- **Severidade**: MEDIUM
- **Arquivos**: Todos
- **Descrição**: Sem docstrings, sem type hints, sem comentários
- **Impacto**: Alto custo de onboarding, sem autocompletar, fácil usar funções incorretamente
- **Recomendação**: Adicionar docstrings, type hints, usar mypy

---

### LOW - Melhorias de Qualidade (4)

#### 1.17 Nomenclatura Pobre de Variáveis
- **Severidade**: LOW
- **Arquivo**: `models.py`
- **Descrição**: Nomes genéricos reduzem clareza
- **Exemplos**: `row`, `cursor2`, `prod`
- **Recomendação**: Usar nomes descritivos e específicos do domínio

#### 1.18 Import Não Utilizado
- **Severidade**: LOW
- **Arquivo**: `models.py` (linha 2)
- **Descrição**: `sqlite3` importado mas nunca usado
- **Recomendação**: Remover imports não utilizados

#### 1.19 Estado Global de Conexão com Banco
- **Severidade**: LOW
- **Arquivo**: `database.py` (linhas 4-10)
- **Descrição**: Estado mutável global para conexão de BD
- **Impacto**: Testes difíceis, problemas de thread safety
- **Recomendação**: Usar context de aplicação, connection pooling, injeção de dependência

#### 1.20 Códigos de Resposta HTTP Inadequados
- **Severidade**: LOW
- **Arquivo**: `controllers.py`
- **Descrição**: Alguns endpoints usam 500 genérico para erros de lógica de negócio
- **Impacto**: Clientes de API não conseguem distinguir erros de servidor de erros de cliente
- **Recomendação**: 400 para validação, 500 apenas para erros inesperados

---

## Projeto 2: ecommerce-api-legacy (Node.js/Express LMS API)

### Contexto
- **Stack**: Node.js + Express 4.x
- **Domínio**: LMS API com fluxo de checkout (cursos, matrículas, pagamentos)
- **Arquitetura**: Monolítica - 3 arquivos em src/
- **Arquivos**: app.js, AppManager.js, utils.js
- **Linhas de código**: ~200 LOC

---

### CRITICAL - Problemas Críticos (5)

#### 2.1 Credenciais de Produção Hardcoded
- **Severidade**: CRITICAL
- **Arquivo**: `src/utils.js` (linhas 2-6)
- **Descrição**: Credenciais de produção (senha de BD, chave de payment gateway) hardcoded no código
- **Exemplo**:
  ```javascript
  const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br"
  };
  ```
- **Impacto**: Qualquer pessoa com acesso ao repositório pode acessar BD de produção, sistemas de pagamento e email. Viola PCI-DSS, SOC2, GDPR
- **Recomendação**: Mover para variáveis de ambiente, usar dotenv, secrets management (AWS Secrets Manager, HashiCorp Vault)

#### 2.2 Criptografia Trivial/Quebrada
- **Severidade**: CRITICAL
- **Arquivo**: `src/utils.js` (linhas 17-23)
- **Descrição**: "Hash" de senha é apenas base64 encoding repetido, completamente reversível
- **Exemplo**:
  ```javascript
  function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
      hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
  }
  ```
- **Impacto**: Senhas podem ser crackeadas instantaneamente. Violação de padrões de autenticação
- **Recomendação**: Usar bcrypt, argon2 ou scrypt. Nunca implementar criptografia customizada

#### 2.3 Armazenamento de Senhas em Texto Plano
- **Severidade**: CRITICAL
- **Arquivo**: `src/AppManager.js` (linha 18)
- **Descrição**: Senhas de usuário armazenadas em plaintext no seed
- **Exemplo**:
  ```javascript
  this.db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
  ```
- **Impacto**: Comprometimento completo de contas seeded, senhas visíveis em BD/logs/backups
- **Recomendação**: Hash todas as senhas antes de armazenar

#### 2.4 Processamento de Cartão Sem Validação - Violação PCI-DSS
- **Severidade**: CRITICAL
- **Arquivo**: `src/AppManager.js` (linhas 28-48)
- **Descrição**: Processamento de cartão de crédito sem validação alguma. Dados de cartão em texto plano
- **Exemplo**:
  ```javascript
  app.post('/api/checkout', (req, res) => {
    let cc = req.body.card;
    // Apenas checagem de null
    if (!cc) return res.status(400).send("Bad Request");
    // Sem validação de formato, sem Luhn algorithm
    let status = cc.startsWith("4") ? "PAID" : "DENIED";
  ```
- **Impacto**: Violação PCI-DSS, risco de fraude, armazenamento de dados de cartão viola regulamentações, responsabilidade legal
- **Recomendação**: Usar payment gateway (Stripe, PayPal), nunca armazenar dados de cartão raw, implementar validação e tokenização

#### 2.5 Exposição de Chave de API e Cartão em Logs
- **Severidade**: CRITICAL
- **Arquivo**: `src/AppManager.js` (linha 45)
- **Descrição**: Número completo de cartão e chave live de API são logados em stdout
- **Exemplo**:
  ```javascript
  console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
  ```
- **Impacto**: Credenciais e PII expostas, logs capturados em sistemas de monitoramento, violação PCI-DSS
- **Recomendação**: Nunca logar dados sensíveis, implementar logging estruturado com redação

---

### HIGH - Problemas Graves (4)

#### 2.6 God Class - AppManager Viola SRP
- **Severidade**: HIGH
- **Arquivo**: `src/AppManager.js` (linhas 4-142)
- **Descrição**: Classe única gerencia: inicialização de BD, setup de rotas, lógica de checkout, lógica de relatórios financeiros, deleção de usuários
- **Impacto**: Impossível testar/estender/manter, mudanças afetam tudo, sem reuso de código, alto acoplamento com Express
- **Recomendação**: Separar em camadas: Controllers (routing), Services (business logic), Repositories (data access), Models (entities)

#### 2.7 Callback Hell / Pyramid of Doom
- **Severidade**: HIGH
- **Arquivo**: `src/AppManager.js` (linhas 80-129)
- **Descrição**: 7+ níveis de callbacks aninhados
- **Exemplo**:
  ```javascript
  this.db.all("SELECT * FROM courses", [], (err, courses) => {
    courses.forEach(c => {
      this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
        enrollments.forEach(enr => {
          this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], (err, user) => {
            this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enr.id], (err, payment) => {
              // ... profundamente aninhado
  ```
- **Impacto**: Código não manutenível, tratamento de erro inconsistente, race conditions, impossível testar
- **Recomendação**: Usar promises ou async/await, bibliotecas de BD com suporte a promises (better-sqlite3, Knex.js)

#### 2.8 Acoplamento Forte ao Framework Express
- **Severidade**: HIGH
- **Arquivo**: `src/AppManager.js` (linhas 25-138)
- **Descrição**: Lógica de negócio embedded diretamente em route handlers do Express
- **Impacto**: Lógica não pode ser testada sem Express, não pode usar em contextos diferentes (CLI, jobs), viola padrão MVC
- **Recomendação**: Extrair para service classes, controllers só gerenciam HTTP

#### 2.9 Falta de Validação e Tratamento de Erros
- **Severidade**: HIGH
- **Arquivo**: `src/AppManager.js` (múltiplas localizações)
- **Descrição**:
  - Linha 35: Apenas checa presença, não formato/validade
  - Linha 40-41: Erro genérico de BD não diferencia tipos de erro
  - Sem validação de email (linha 30)
  - Sem requisitos de força de senha (linha 31)
  - Erros inconsistentes: "Bad Request", "Erro DB", "Erro Matrícula"
- **Impacto**: Corrupção de dados, estados inválidos no BD, UX ruim, impossível debugar
- **Recomendação**: Validação centralizada, formato de erro consistente, códigos HTTP apropriados

---

### MEDIUM - Problemas Moderados (3)

#### 2.10 Problema N+1 de Queries
- **Severidade**: MEDIUM
- **Arquivo**: `src/AppManager.js` (linhas 89-126)
- **Descrição**: Para buscar relatório financeiro de C cursos com E matrículas: 1 + C + (C×E) + (C×E) = O(C×E) queries
- **Análise**: 100 cursos, 50 matrículas cada = ~10.000+ queries para um único relatório
- **Impacto**: Degradação severa de performance, BD vira gargalo
- **Recomendação**: Usar SQL JOINs para buscar tudo em query única ou batch loads

#### 2.11 Race Condition - Transação Ausente em Checkout
- **Severidade**: MEDIUM
- **Arquivo**: `src/AppManager.js` (linhas 50-62)
- **Descrição**: Três INSERTs separados sem transação de BD
- **Exemplo**:
  ```javascript
  this.db.run("INSERT INTO enrollments ...", function(err) {  // 1
    let enrId = this.lastID;
    self.db.run("INSERT INTO payments ...", function(err) {   // 2
      self.db.run("INSERT INTO audit_logs ...", (err) => {    // 3
  ```
- **Impacto**: Se falhar no meio (crash, network), BD fica inconsistente (matrícula sem pagamento, pagamento sem audit log)
- **Recomendação**: Usar transações de BD (BEGIN TRANSACTION; COMMIT;)

#### 2.12 Problema de Integridade - Foreign Keys Ausentes
- **Severidade**: MEDIUM
- **Arquivo**: `src/AppManager.js` (linhas 12-16)
- **Descrição**: Sem constraints de foreign key, sem integridade referencial
- **Exemplo**:
  ```javascript
  this.db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
  // Sem FOREIGN KEY constraints
  ```
- **Impacto**: Registros órfãos, dados inconsistentes, delete de usuário (133-136) deixa matrículas/pagamentos "sujas"
- **Recomendação**: Habilitar foreign key constraints, implementar cascading delete ou soft deletes

---

### LOW - Melhorias de Qualidade (3)

#### 2.13 Nomenclatura Pobre de Variáveis
- **Severidade**: LOW
- **Arquivo**: `src/AppManager.js` (linhas 29-32)
- **Descrição**: Variáveis de uma letra e nomes crípticos
- **Exemplos**: `u`, `e`, `p`, `cid`, `cc` (ambíguo)
- **Recomendação**: Usar nomes descritivos: `username`, `email`, `password`, `courseId`, `cardNumber`

#### 2.14 Magic Numbers e Valores Hardcoded
- **Severidade**: LOW
- **Arquivos**: `src/utils.js` (linha 19), `AppManager.js` (linha 46)
- **Descrição**:
  - `10000` iterações de loop - por quê?
  - `substring(0, 2)` - por que 2?
  - `cc.startsWith("4")` - assume apenas Visa válido
- **Impacto**: Código não manutenível, regras de negócio espalhadas
- **Recomendação**: Extrair para constantes nomeadas, adicionar comentários

#### 2.15 Potencial Vulnerabilidade XSS
- **Severidade**: LOW
- **Arquivo**: `src/AppManager.js` (linha 57)
- **Descrição**: Queries parametrizadas (bom), mas se dados forem renderizados em HTML sem encoding, XSS possível
- **Impacto**: XSS potencial se audit logs renderizados em UI web
- **Recomendação**: Sempre fazer HTML-encoding ao renderizar, usar template engines que auto-escapam

---

## Projeto 3: task-manager-api (Python/Flask Task Manager)

### Contexto
- **Stack**: Python 3.x + Flask + SQLAlchemy
- **Domínio**: API de Task Manager (tarefas, usuários, categorias)
- **Arquitetura**: Semi-organizada com camadas (models/, routes/, services/, utils/)
- **Arquivos**: app.py, database.py, seed.py + 4 models, 3 routers, 1 service, helpers
- **Linhas de código**: ~600 LOC
- **Observação**: Projeto já possui alguma organização, mas ainda tem problemas graves

---

### CRITICAL - Problemas Críticos (4)

#### 3.1 Secret Key Hardcoded
- **Severidade**: CRITICAL
- **Arquivo**: `app.py` (linha 13)
- **Descrição**: Flask SECRET_KEY hardcoded como placeholder fraco
- **Exemplo**:
  ```python
  app.config['SECRET_KEY'] = 'super-secret-key-123'
  ```
- **Impacto**: Tokens de sessão podem ser forjados, tokens CSRF bypassados, validação JWT comprometida
- **Recomendação**: Carregar de variáveis de ambiente usando `os.environ.get('SECRET_KEY')`, gerar chaves fortes (min 32 bytes)

#### 3.2 Credenciais de Email Hardcoded
- **Severidade**: CRITICAL
- **Arquivo**: `services/notification_service.py` (linhas 9-10)
- **Descrição**: Credenciais SMTP hardcoded com senha fraca
- **Exemplo**:
  ```python
  self.email_user = 'taskmanager@gmail.com'
  self.email_password = 'senha123'
  ```
- **Impacto**: Atacante pode enviar emails se passando pela aplicação, conta pode ser sequestrada
- **Recomendação**: Usar variáveis de ambiente, secrets management, usar `.env` (python-dotenv já em requirements.txt mas não usado)

#### 3.3 Hash de Senha com MD5 (Quebrado)
- **Severidade**: CRITICAL
- **Arquivo**: `models/user.py` (linhas 27-32)
- **Descrição**: MD5 usado para hash de senha. MD5 é criptograficamente quebrado, sem salt
- **Exemplo**:
  ```python
  def set_password(self, pwd):
      self.password = hashlib.md5(pwd.encode()).hexdigest()

  def check_password(self, pwd):
      return self.password == hashlib.md5(pwd.encode()).hexdigest()
  ```
- **Impacto**: Senhas crackeadas em minutos com rainbow tables, todas as contas comprometidas se BD vazar, não-compliant com OWASP/PCI-DSS
- **Recomendação**: Usar `bcrypt`, `argon2`, ou `scrypt`. Flask-Bcrypt é padrão. Mínimo 12 rounds

#### 3.4 Senha Exposta em Resposta de API
- **Severidade**: CRITICAL
- **Arquivo**: `models/user.py` (linhas 16-25)
- **Descrição**: Hash de senha incluído em toda resposta de API
- **Exemplo**:
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
- **Impacto**: Hashes vazados para todos os consumidores de API, permite ataques offline, violação de compliance (PCI-DSS, GDPR)
- **Recomendação**: Remover 'password' de `to_dict()`, criar métodos separados para contextos diferentes

---

### HIGH - Problemas Graves (4)

#### 3.5 Ausência de Autenticação/Autorização
- **Severidade**: HIGH
- **Arquivos**: Todas as rotas (`task_routes.py`, `user_routes.py`, `report_routes.py`)
- **Descrição**: Todos os endpoints são publicamente acessíveis. Login existe mas token nunca é validado
- **Exemplo**:
  ```python
  # user_routes.py:210
  'token': 'fake-jwt-token-' + str(user.id)  # Token fake!
  ```
- **Impacto**: Usuários não autenticados podem acessar todos os dados, usuários podem modificar dados de outros (IDOR), bypass completo de autorização
- **Recomendação**: Implementar middleware de autenticação com decorator, usar Flask-JWT-Extended, checar token em todo endpoint, implementar RBAC

#### 3.6 Tratamento de Erros Impróprio
- **Severidade**: HIGH
- **Arquivos**: `routes/task_routes.py` (linhas 62-63, 149-154)
- **Descrição**: Bare `except:` captura TODAS as exceções silenciosamente, logging via print
- **Exemplo**:
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
- **Impacto**: Erros falham silenciosamente, sem stack traces para debug, logs poluídos com prints
- **Recomendação**: Usar módulo `logging`, capturar exceções específicas, logar tracebacks completos, error handlers configurados

#### 3.7 Lógica de Negócio em Route Handlers
- **Severidade**: HIGH
- **Arquivos**: `task_routes.py` (linhas 11-63), `report_routes.py` (linhas 12-101)
- **Descrição**: Cálculo de overdue duplicado 4+ vezes, serialização manual, queries em routes
- **Exemplo**:
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
- **Duplicação**: Cálculo de overdue em `task_routes.py:30-39`, `task_routes.py:71-80`, `user_routes.py:171-180`, `report_routes.py:132-135`
- **Impacto**: Viola SRP, impossível testar lógica sem HTTP, código duplicado, não pode reutilizar em outros contextos
- **Recomendação**: Extrair para TaskService, mover cálculo de overdue para Task model ou service, usar marshmallow para serialização

#### 3.8 Bare Except Clause
- **Severidade**: HIGH
- **Arquivos**: `user_routes.py:130`, `task_routes.py:62`, `report_routes.py:187, 207, 223`
- **Descrição**: `except:` sem tipo captura SystemExit, KeyboardInterrupt
- **Impacto**: Debug extremamente difícil, mascara erros críticos de sistema, aplicação não desliga cleanly
- **Recomendação**: Ser específico: `except (IntegrityError, DataError) as e:`

---

### MEDIUM - Problemas Moderados (2)

#### 3.9 Requisitos de Senha Inseguros
- **Severidade**: MEDIUM
- **Arquivos**: `routes/user_routes.py` (linhas 64-65), `utils/helpers.py` (linha 114)
- **Descrição**: Senha mínima de apenas 4 caracteres, sem requisitos de complexidade
- **Exemplo**:
  ```python
  if len(password) < 4:
      return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400

  # seed.py:19, 26, 33
  u1.set_password('1234')
  u2.set_password('abcd')
  u3.set_password('pass')
  ```
- **Impacto**: Ataques de força bruta triviais, ataques de dicionário bem-sucedidos, credenciais seed em produção comprometem contas
- **Recomendação**: Mínimo 12 caracteres, requerer mix de uppercase/lowercase/números/especiais, guidelines NIST/OWASP

#### 3.10 Endpoint de Search Vulnerável (LIKE Injection)
- **Severidade**: MEDIUM
- **Arquivo**: `routes/task_routes.py` (linhas 240-271)
- **Descrição**: LIKE operator sem sanitização de caracteres especiais
- **Exemplo**:
  ```python
  query = request.args.get('q', '')
  tasks = tasks.filter(
      db.or_(
          Task.title.like(f'%{query}%'),
          Task.description.like(f'%{query}%')
      )
  )
  ```
- **Impacto**: Usuário pode usar `%` para wildcards além da intenção, disclosure de informação, degradação de performance, sem rate limiting
- **Recomendação**: Escapar caracteres LIKE: `query.replace('%', '\\%').replace('_', '\\_')`, considerar full-text search, rate limiting, paginação

---

### LOW - Melhorias de Qualidade (1)

#### 3.11 Magic Numbers e Constantes Não Centralizadas
- **Severidade**: LOW
- **Arquivos**: Espalhados por routes e models
- **Descrição**: Range de prioridade (`1` e `5`), valores de status (`['pending', 'in_progress', 'done', 'cancelled']`), separador de tags (`','`), formato de data (`'%Y-%m-%d'`) duplicados
- **Exemplos**:
  - `task_routes.py:110`: `if status not in ['pending', 'in_progress', 'done', 'cancelled']`
  - `task_routes.py:113`: `if priority < 1 or priority > 5`
  - `helpers.py:110-115`: Constantes definidas mas não usadas em todo lugar
  - `models/task.py:39`: Mesma lista de status hardcoded novamente
- **Impacto**: Mudanças requerem atualizar múltiplos arquivos, risco de inconsistência, menos legível
- **Recomendação**: Consolidar em `constants.py` ou `config.py`, importar e usar consistentemente

---

## Padrões Comuns Identificados (Base para a Skill)

### Anti-Patterns Encontrados (Catálogo para Skill)

| Anti-Pattern | Severidade | Projetos Afetados | Sinais de Detecção |
|--------------|-----------|-------------------|-------------------|
| SQL Injection | CRITICAL | 1, 2 | String concatenation em queries, `execute()` com `+` ou `f-string` |
| Hardcoded Credentials | CRITICAL | 1, 2, 3 | `SECRET_KEY =`, `password =`, `dbPass:` em código |
| Weak Cryptography | CRITICAL | 2, 3 | `md5()`, `base64`, custom crypto functions |
| Plaintext Passwords | CRITICAL | 1, 2, 3 | Senhas sem hash, comparação direta |
| Missing Authentication | HIGH | 1, 2, 3 | Rotas sem decorators, sem token validation |
| God Class | HIGH | 1, 2 | Classe/arquivo com 300+ linhas, múltiplas responsabilidades |
| Callback Hell | HIGH | 2 | 5+ níveis de aninhamento de callbacks |
| N+1 Queries | HIGH | 1, 2 | Queries dentro de loops, sem JOINs |
| Business Logic in Routes | HIGH | 1, 2, 3 | Lógica de negócio em route handlers |
| Tight Coupling | MEDIUM | 1, 2, 3 | Direct imports sem injeção de dependência |
| Missing Validation | MEDIUM | 1, 2, 3 | Endpoints sem validação de input |
| Bare Except | MEDIUM | 3 | `except:` sem tipo de exceção |
| Magic Numbers | LOW | 1, 2, 3 | Valores hardcoded sem constantes nomeadas |
| Poor Naming | LOW | 1, 2, 3 | Variáveis de uma letra, nomes genéricos |

### Transformações de Refatoração (Playbook para Skill)

| Transformação | De (Anti-Pattern) | Para (MVC Pattern) |
|---------------|-------------------|-------------------|
| 1. Extrair Configuração | Secrets hardcoded em código | `.env` + `os.getenv()` + `config/settings.py` |
| 2. Parametrizar Queries | String concatenation | Parameterized queries ou ORM |
| 3. Adicionar Hash de Senha | Plaintext/MD5 | bcrypt/argon2 com salt |
| 4. Separar Camadas | God Class | Models + Controllers + Services |
| 5. Adicionar Autenticação | Sem auth | JWT middleware + decorators |
| 6. Otimizar Queries | N+1 queries | JOINs ou eager loading |
| 7. Async/Await | Callback hell | Promises/async-await |
| 8. Validação Centralizada | Validação espalhada | Schema validation (marshmallow/joi) |

---

## Conclusões para Criação da Skill

### Achados Principais

1. **Problemas de Segurança** são os mais críticos e comuns (14 CRITICAL)
   - SQL Injection, credenciais hardcoded, senhas fracas aparecem nos 3 projetos

2. **Violações Arquiteturais** são consistentes (13 HIGH)
   - God Classes, falta de separação de camadas, sem autenticação são universais

3. **Problemas de Performance** são recorrentes
   - N+1 queries aparecem em 2 de 3 projetos

4. **Code Smells** são menos críticos mas indicam má manutenibilidade
   - Magic numbers, poor naming, duplicação de código

### Recomendações para a Skill

A skill `/refactor-arch` deve:

1. **Fase 1 - Análise**:
   - Detectar linguagem/framework por imports e package.json/requirements.txt
   - Mapear estrutura de diretórios atual
   - Identificar domínio por nomes de tabelas/models

2. **Fase 2 - Auditoria**:
   - Priorizar detecção de CRITICAL (segurança)
   - Buscar patterns de string concatenation em SQL
   - Identificar hardcoded secrets via regex
   - Detectar ausência de auth middleware
   - Encontrar God Classes (LOC > 200, múltiplas responsabilidades)

3. **Fase 3 - Refatoração**:
   - Criar estrutura MVC:
     ```
     src/
     ├── config/
     ├── models/
     ├── views/ (ou routes/)
     ├── controllers/ (ou services/)
     ├── middlewares/
     └── app.py
     ```
   - Extrair configurações para `.env`
   - Substituir queries por parametrizadas
   - Adicionar auth middleware
   - Separar business logic de routes

### Próximos Passos

1. ✅ Análise manual completa (ESTE DOCUMENTO)
2. ⏭️ Criar `.claude/skills/refactor-arch/SKILL.md`
3. ⏭️ Criar arquivos de referência:
   - `anti-patterns-catalog.md`
   - `refactoring-playbook.md`
   - `mvc-guidelines.md`
   - `audit-report-template.md`
   - `project-analysis-heuristics.md`
4. ⏭️ Executar skill nos 3 projetos
5. ⏭️ Gerar relatórios de auditoria
6. ⏭️ Iterar e refinar

---

**Documento gerado**: 2026-08-09
**Total de achados**: 46 problemas identificados
**Projetos analisados**: 3/3 ✅
