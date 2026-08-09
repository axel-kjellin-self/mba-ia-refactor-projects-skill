# Project Analysis Heuristics

Este documento contém heurísticas para detectar automaticamente linguagem, framework, banco de dados e arquitetura de projetos.

---

## 1. Detecção de Linguagem

### Python
**Sinais Primários**:
- Arquivo `requirements.txt` presente
- Arquivo `setup.py` presente
- Arquivo `pyproject.toml` presente
- Arquivos `.py` no projeto
- Diretórios `__pycache__/`, `*.egg-info/`

**Sinais Secundários**:
- Imports Python: `import`, `from ... import`
- Syntax: `def`, `class`, indentação significativa
- Virtualenv: `venv/`, `.venv/`, `env/`

**Versão**:
- Checar `python_requires` em `setup.py`
- Checar runtime em `runtime.txt`
- Padrão: assumir Python 3.x

---

### JavaScript/Node.js
**Sinais Primários**:
- Arquivo `package.json` presente
- Arquivo `package-lock.json` ou `yarn.lock` presente
- Arquivos `.js`, `.mjs`, `.cjs` no projeto
- Diretório `node_modules/`

**Sinais Secundários**:
- Imports: `require()`, `import ... from`
- `const`, `let`, arrow functions `=>`
- Script `npm start`, `npm test` em package.json

**Versão**:
- Checar `"engines": { "node": "..." }` em package.json
- Padrão: assumir Node.js 14+

---

### TypeScript
**Sinais Primários**:
- Arquivo `tsconfig.json` presente
- Arquivos `.ts`, `.tsx` no projeto
- `typescript` em devDependencies do package.json

**Sinais Secundários**:
- Type annotations: `variable: type`
- Interfaces e types

---

### Java
**Sinais Primários**:
- Arquivo `pom.xml` (Maven) ou `build.gradle` (Gradle)
- Arquivos `.java` no projeto
- Estrutura `src/main/java/`

**Sinais Secundários**:
- Package declarations: `package com.example;`
- Imports: `import java.util.*;`

---

### PHP
**Sinais Primários**:
- Arquivo `composer.json` presente
- Arquivos `.php` no projeto
- Tag de abertura `<?php`

---

### Ruby
**Sinais Primários**:
- Arquivo `Gemfile` presente
- Arquivos `.rb` no projeto
- `require 'bundler'`

---

## 2. Detecção de Framework

### Python Frameworks

#### Flask
**Sinais**:
- `flask` em requirements.txt
- Import: `from flask import Flask`
- Padrão: `app = Flask(__name__)`
- Decorators: `@app.route()`

**Versão**:
```python
# requirements.txt
Flask==3.1.1  # Versão explícita
```

#### Django
**Sinais**:
- `django` em requirements.txt
- Arquivo `manage.py` presente
- Diretório com `settings.py`, `urls.py`, `wsgi.py`
- Import: `from django.`

#### FastAPI
**Sinais**:
- `fastapi` em requirements.txt
- Import: `from fastapi import FastAPI`
- `app = FastAPI()`
- Type hints em rotas

---

### JavaScript Frameworks

#### Express.js
**Sinais**:
- `express` em package.json dependencies
- Import: `const express = require('express')` ou `import express from 'express'`
- `app.get()`, `app.post()` patterns
- `app.listen()`

**Versão**:
```json
// package.json
"dependencies": {
  "express": "^4.18.0"
}
```

#### NestJS
**Sinais**:
- `@nestjs/core` em dependencies
- Decorators: `@Controller()`, `@Module()`
- Arquivos `.controller.ts`, `.service.ts`

#### Koa
**Sinais**:
- `koa` em dependencies
- `const Koa = require('koa')`
- `app.use(async ctx => {})`

---

### Outros Frameworks

#### Ruby on Rails
**Sinais**:
- `rails` em Gemfile
- Diretórios `app/models/`, `app/controllers/`, `app/views/`
- Arquivo `config/routes.rb`

#### Spring Boot (Java)
**Sinais**:
- `spring-boot-starter` em pom.xml
- Annotations: `@SpringBootApplication`, `@RestController`

#### ASP.NET Core (C#)
**Sinais**:
- Arquivo `.csproj` com `Microsoft.AspNetCore`
- `Program.cs`, `Startup.cs`

---

## 3. Detecção de Banco de Dados

### SQLite
**Sinais**:
- Arquivo `.db` ou `.sqlite` presente
- Import Python: `import sqlite3`
- Connection string: `sqlite:///`
- Node: `require('sqlite3')`

### PostgreSQL
**Sinais**:
- `psycopg2` (Python) ou `pg` (Node) em dependencies
- Connection string: `postgresql://` ou `postgres://`
- Variável de ambiente: `DATABASE_URL` com postgres

### MySQL/MariaDB
**Sinais**:
- `mysql-connector-python` ou `PyMySQL` (Python)
- `mysql2` ou `mysql` (Node) em dependencies
- Connection string: `mysql://`

### MongoDB
**Sinais**:
- `pymongo` (Python) ou `mongodb` (Node)
- Connection string: `mongodb://` ou `mongodb+srv://`

### Redis
**Sinais**:
- `redis` em dependencies
- Connection: `redis://`

---

## 4. Detecção de ORM/Query Builder

### Python

#### SQLAlchemy
**Sinais**:
- `sqlalchemy` em requirements.txt
- Import: `from sqlalchemy import`
- `db.Model`, `db.Column`

#### Django ORM
**Sinais**:
- Django framework + `models.py` com classes herdando `models.Model`

### JavaScript

#### Sequelize
**Sinais**:
- `sequelize` em dependencies
- `Model.findAll()`, `Model.create()`

#### TypeORM
**Sinais**:
- `typeorm` em dependencies
- Decorators: `@Entity()`, `@Column()`

#### Prisma
**Sinais**:
- `prisma` em dependencies
- Arquivo `schema.prisma` presente

---

## 5. Detecção de Arquitetura

### Monolítica (No Structure)
**Sinais**:
- 1-5 arquivos principais no root
- Tudo em um ou dois arquivos enormes (200+ linhas)
- Sem separação de diretórios por responsabilidade
- Nomes genéricos: `app.py`, `main.js`, `server.js`

**Indicadores**:
- Queries SQL + lógica de negócio + rotas no mesmo arquivo
- Nenhum diretório `models/`, `controllers/`, `services/`

**Exemplo**:
```
project/
├── app.py          # 300+ linhas com tudo
├── database.py     # Setup de BD
└── requirements.txt
```

---

### Semi-Organizada (Partial Layers)
**Sinais**:
- Alguns diretórios de separação presentes
- Diretórios: `models/`, `routes/`, `utils/`
- Mas falta `controllers/` ou `services/`
- Lógica de negócio ainda em route handlers

**Indicadores**:
- Models bem definidos
- Routes existem mas contêm lógica de negócio
- Sem service layer

**Exemplo**:
```
project/
├── models/         # Models organizados
├── routes/         # Routes com lógica dentro
├── utils/          # Helpers
└── app.py
```

---

### MVC Básico
**Sinais**:
- Diretórios: `models/`, `views/` (ou `routes/`), `controllers/`
- Separação clara de responsabilidades
- Pode faltar `services/` para lógica complexa

**Exemplo**:
```
project/
├── models/
├── views/
├── controllers/
└── app.py
```

---

### MVC + Service Layer (Well-Structured)
**Sinais**:
- Diretórios: `models/`, `views/`, `controllers/`, `services/`
- Pode ter: `repositories/`, `middlewares/`, `schemas/`
- Config externalizada: `config/`
- Lógica de negócio em services, não em controllers

**Exemplo**:
```
project/
├── config/
├── models/
├── services/
├── controllers/
├── routes/
├── middlewares/
└── app.py
```

---

### Microservices
**Sinais**:
- Múltiplos `package.json` ou `requirements.txt`
- Diretórios por serviço: `user-service/`, `order-service/`
- Docker Compose com múltiplos serviços
- API Gateway presente

---

## 6. Identificação de Domínio

Analise nomes de:
- **Tabelas/Collections**: Indicam entidades principais
- **Models**: Classes/arquivos em `models/`
- **Routes**: Endpoints da API
- **Diretórios**: Agrupamento por domínio

### Heurísticas por Domínio

#### E-commerce
**Sinais**:
- Entidades: `products`, `orders`, `cart`, `checkout`, `inventory`, `customers`
- Rotas: `/products`, `/cart`, `/checkout`, `/orders`
- Campos: `price`, `stock`, `sku`, `category`

#### Task Manager / Todo App
**Sinais**:
- Entidades: `tasks`, `users`, `categories`, `tags`
- Rotas: `/tasks`, `/users`, `/categories`
- Campos: `title`, `description`, `status`, `priority`, `due_date`
- Status values: `pending`, `in_progress`, `done`, `cancelled`

#### LMS (Learning Management System)
**Sinais**:
- Entidades: `courses`, `students`, `enrollments`, `lessons`, `assignments`
- Rotas: `/courses`, `/enrollments`, `/lessons`
- Campos: `course_id`, `student_id`, `grade`, `progress`

#### Blog/CMS
**Sinais**:
- Entidades: `posts`, `authors`, `comments`, `categories`, `tags`
- Rotas: `/posts`, `/comments`, `/authors`
- Campos: `title`, `content`, `published_at`

#### Authentication/User Management
**Sinais**:
- Entidades: `users`, `roles`, `permissions`, `sessions`
- Rotas: `/login`, `/register`, `/logout`, `/users`
- Campos: `email`, `password`, `role`, `token`

#### Financial/Accounting
**Sinais**:
- Entidades: `transactions`, `accounts`, `invoices`, `payments`
- Rotas: `/transactions`, `/invoices`, `/payments`
- Campos: `amount`, `balance`, `currency`, `date`

---

## 7. Análise de Dependências

### Python (requirements.txt)
```python
# Parsear requirements.txt
with open('requirements.txt') as f:
    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Extrair nome e versão
for dep in deps:
    if '==' in dep:
        name, version = dep.split('==')
    else:
        name, version = dep, 'latest'
```

**Principais dependências**:
- `flask`: Web framework
- `sqlalchemy`: ORM
- `marshmallow`: Validação
- `flask-cors`: CORS
- `python-dotenv`: Variáveis de ambiente
- `bcrypt`: Hash de senhas
- `pyjwt`: JWT

### JavaScript (package.json)
```javascript
// Ler package.json
const pkg = require('./package.json');

// Dependencies de produção
const deps = pkg.dependencies;

// DevDependencies
const devDeps = pkg.devDependencies;
```

**Principais dependências**:
- `express`: Web framework
- `sequelize`: ORM
- `bcrypt`: Hash de senhas
- `jsonwebtoken`: JWT
- `dotenv`: Variáveis de ambiente
- `cors`: CORS
- `joi`: Validação

---

## 8. Contagem de Arquivos e Linhas

### Contar Arquivos de Código
```bash
# Python
find . -name "*.py" -not -path "./venv/*" -not -path "./__pycache__/*" | wc -l

# JavaScript
find . -name "*.js" -not -path "./node_modules/*" | wc -l
```

### Contar Linhas de Código
```bash
# Python
find . -name "*.py" -not -path "./venv/*" | xargs wc -l | tail -1

# JavaScript
find . -name "*.js" -not -path "./node_modules/*" | xargs wc -l | tail -1
```

### Categorização por Tamanho
- **Pequeno**: < 500 LOC
- **Médio**: 500 - 2000 LOC
- **Grande**: 2000 - 10000 LOC
- **Muito Grande**: > 10000 LOC

---

## 9. Detecção de Tabelas do Banco

### SQLite
```python
import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
```

### PostgreSQL/MySQL (via código)
```python
# Procurar por CREATE TABLE em arquivos SQL
# Ou por models em código ORM
```

### A partir de Models (Python/SQLAlchemy)
```python
# Ler arquivos em models/
# Procurar por classes que herdam db.Model
# Nome da classe ou __tablename__ indica nome da tabela
```

### A partir de Models (JavaScript/Sequelize)
```javascript
// Procurar por Model.init() ou sequelize.define()
// Nome do model indica nome da tabela (plural)
```

---

## 10. Template de Saída da Fase 1

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.x
Framework:     Flask 3.1.1
Dependencies:  flask-cors, python-dotenv
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed (~800 lines of code)
DB tables:     produtos, usuarios, pedidos, itens_pedido
DB type:       SQLite
ORM:           None (raw SQL)
================================
```

### Campos Obrigatórios:
1. **Language**: Python, JavaScript, Java, etc. + versão se detectável
2. **Framework**: Flask, Express, Django + versão
3. **Dependencies**: Top 3-5 dependências principais
4. **Domain**: Qual o propósito da aplicação
5. **Architecture**: Descrição da organização atual
6. **Source files**: Número de arquivos e estimativa de LOC
7. **DB tables**: Lista das principais tabelas/entidades

### Campos Opcionais:
- **DB type**: SQLite, PostgreSQL, MySQL, MongoDB
- **ORM**: SQLAlchemy, Sequelize, None
- **Auth**: JWT, Session-based, None
- **API Style**: REST, GraphQL

---

## 11. Detecção de Tecnologias Específicas

### Containerização
- **Docker**: Arquivo `Dockerfile` ou `docker-compose.yml`
- **Kubernetes**: Diretório `k8s/` ou arquivos `.yaml` com `kind: Deployment`

### CI/CD
- **GitHub Actions**: `.github/workflows/`
- **GitLab CI**: `.gitlab-ci.yml`
- **Jenkins**: `Jenkinsfile`

### Testing
- **Python**: `pytest`, `unittest`, diretório `tests/`
- **JavaScript**: `jest`, `mocha`, `chai` em devDependencies

### Linting/Formatting
- **Python**: `black`, `flake8`, `pylint`, `mypy`
- **JavaScript**: `eslint`, `prettier`

---

## 12. Checklist de Análise

- [ ] Linguagem detectada corretamente
- [ ] Framework identificado com versão
- [ ] Banco de dados identificado
- [ ] ORM detectado (se existir)
- [ ] Arquitetura classificada (monolítica, semi-organizada, MVC, etc.)
- [ ] Domínio da aplicação identificado
- [ ] Principais entidades/tabelas listadas
- [ ] Número de arquivos contados
- [ ] Estimativa de linhas de código
- [ ] Dependências principais listadas
- [ ] Resumo formatado impresso

---

## Algoritmo de Análise

```python
def analyze_project(project_path):
    analysis = {}

    # 1. Detectar linguagem
    if exists('requirements.txt'):
        analysis['language'] = 'Python'
        analysis['deps_file'] = 'requirements.txt'
    elif exists('package.json'):
        analysis['language'] = 'JavaScript/Node.js'
        analysis['deps_file'] = 'package.json'

    # 2. Detectar framework
    deps = read_dependencies(analysis['deps_file'])
    if 'flask' in deps:
        analysis['framework'] = f"Flask {deps['flask']}"
    elif 'express' in deps:
        analysis['framework'] = f"Express {deps['express']}"

    # 3. Detectar arquitetura
    has_models = exists('models/') or exists('src/models/')
    has_controllers = exists('controllers/') or exists('src/controllers/')
    has_services = exists('services/') or exists('src/services/')

    if has_models and has_controllers and has_services:
        analysis['architecture'] = "MVC + Service Layer (bem estruturada)"
    elif has_models and has_controllers:
        analysis['architecture'] = "MVC Básico"
    elif has_models:
        analysis['architecture'] = "Semi-organizada (camada de dados separada)"
    else:
        analysis['architecture'] = "Monolítica (sem separação de camadas)"

    # 4. Identificar domínio
    tables = detect_tables()
    analysis['domain'] = identify_domain(tables)
    analysis['tables'] = tables

    # 5. Contar arquivos
    analysis['files_count'] = count_source_files()
    analysis['lines_of_code'] = estimate_loc()

    return analysis
```
