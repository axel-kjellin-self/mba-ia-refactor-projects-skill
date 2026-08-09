# Refactor Architecture Skill

Esta skill automatiza a análise, auditoria e refatoração de projetos legados para o padrão MVC, independente da tecnologia.

## Objetivo

Transformar projetos com problemas de arquitetura, segurança e qualidade de código em aplicações bem estruturadas seguindo o padrão MVC (Model-View-Controller).

## Como Funciona

A skill opera em **3 fases sequenciais**:

1. **Fase 1 - Análise**: Detecta stack, mapeia arquitetura atual
2. **Fase 2 - Auditoria**: Identifica anti-patterns, gera relatório
3. **Fase 3 - Refatoração**: Reestrutura para MVC, valida funcionamento

---

## FASE 1: ANÁLISE DO PROJETO

### Objetivo
Entender a stack tecnológica, arquitetura atual e domínio da aplicação.

### Tarefas

1. **Detectar Linguagem e Framework**
   - Consulte `project-analysis-heuristics.md` para heurísticas de detecção
   - Analise arquivos de dependências (package.json, requirements.txt, etc.)
   - Identifique a linguagem por extensões de arquivos e imports
   - Determine o framework principal (Flask, Express, Django, etc.)

2. **Mapear Arquitetura Atual**
   - Conte arquivos de código-fonte
   - Identifique estrutura de diretórios
   - Detecte se há separação de camadas ou se é monolítico
   - Liste tabelas/entidades do banco de dados

3. **Identificar Domínio**
   - Analise nomes de models, tabelas, rotas
   - Identifique o propósito da aplicação (e-commerce, task manager, LMS, etc.)

4. **Imprimir Resumo**
   ```
   ================================
   PHASE 1: PROJECT ANALYSIS
   ================================
   Language:      <linguagem>
   Framework:     <framework e versão>
   Dependencies:  <principais dependências>
   Domain:        <domínio da aplicação>
   Architecture:  <descrição da arquitetura atual>
   Source files:  <número de arquivos analisados>
   DB tables:     <lista de tabelas principais>
   ================================
   ```

---

## FASE 2: AUDITORIA ARQUITETURAL

### Objetivo
Identificar todos os anti-patterns, code smells e problemas de segurança, gerando um relatório estruturado.

### Tarefas

1. **Carregar Catálogo de Anti-Patterns**
   - Consulte `anti-patterns-catalog.md` para lista completa de problemas a detectar
   - Cada anti-pattern tem sinais de detecção específicos

2. **Analisar Código em Busca de Problemas**
   - Leia TODOS os arquivos de código-fonte
   - Para cada anti-pattern do catálogo, procure os sinais de detecção
   - Registre arquivo e linha EXATA de cada problema encontrado
   - Classifique por severidade (CRITICAL, HIGH, MEDIUM, LOW)

3. **Gerar Relatório de Auditoria**
   - Use o template em `audit-report-template.md`
   - Liste TODOS os findings com:
     - Severidade
     - Arquivo e linhas exatas
     - Descrição do problema
     - Impacto
     - Recomendação de correção
   - Ordene por severidade (CRITICAL → LOW)
   - Inclua contagem total por severidade

4. **Exibir Relatório e Pausar**
   - Imprima o relatório completo
   - **IMPORTANTE**: Pergunte ao usuário se deseja prosseguir para Fase 3
   - Aguarde confirmação explícita (y/n) antes de modificar qualquer arquivo

### Formato do Relatório

Consulte `audit-report-template.md` para o formato completo.

---

## FASE 3: REFATORAÇÃO PARA MVC

### Objetivo
Reestruturar o projeto para o padrão MVC, eliminando os problemas encontrados na auditoria.

### ⚠️ IMPORTANTE
Esta fase só deve ser executada após aprovação explícita do usuário na Fase 2.

### Tarefas

1. **Consultar Guidelines de Arquitetura**
   - Use `mvc-guidelines.md` para estrutura alvo
   - Use `refactoring-playbook.md` para transformações específicas

2. **Criar Estrutura de Diretórios MVC**
   - Criar pastas conforme o padrão da linguagem:
     - Python/Flask: `src/config/`, `src/models/`, `src/views/`, `src/controllers/`, `src/middlewares/`
     - Node.js/Express: `src/config/`, `src/models/`, `src/routes/`, `src/controllers/`, `src/middlewares/`
   - Manter compatibilidade com convenções do framework

3. **Aplicar Transformações**
   Para cada problema encontrado na Fase 2, aplique a transformação correspondente do playbook:

   - **CRITICAL: Hardcoded Secrets** → Extrair para `.env` + `config/settings`
   - **CRITICAL: SQL Injection** → Substituir por queries parametrizadas
   - **CRITICAL: Weak Crypto** → Implementar bcrypt/argon2
   - **HIGH: God Class** → Separar em Models + Controllers + Services
   - **HIGH: Missing Auth** → Adicionar middleware de autenticação
   - **HIGH: N+1 Queries** → Otimizar com JOINs ou eager loading
   - **MEDIUM: Missing Validation** → Adicionar schema validation
   - **LOW: Magic Numbers** → Extrair para constantes

4. **Mover Código para Camadas Apropriadas**

   **Models** (camada de dados):
   - Definições de entidades/schemas
   - Queries de acesso a dados (Repository pattern)
   - Sem lógica de negócio, sem HTTP

   **Controllers** (camada de orquestração):
   - Recebem requests HTTP
   - Validam inputs
   - Delegam para services
   - Formatam responses
   - Tratam erros HTTP

   **Services** (camada de negócio):
   - Lógica de negócio pura
   - Orquestram múltiplos repositories
   - Transações
   - Regras de domínio
   - Sem dependência de HTTP

   **Views/Routes** (camada de apresentação):
   - Definição de rotas
   - Mapeamento URL → Controller
   - Middlewares de rota

   **Config** (camada de configuração):
   - Carregamento de variáveis de ambiente
   - Configurações da aplicação
   - Constantes globais

   **Middlewares**:
   - Autenticação
   - Error handling global
   - Logging
   - CORS

5. **Criar Arquivo de Configuração**
   - Criar `.env.example` com variáveis necessárias
   - Criar `config/settings.py` ou `config/index.js`
   - Carregar secrets de variáveis de ambiente

6. **Adicionar Error Handling Centralizado**
   - Criar middleware de error handling
   - Usar logging estruturado (não print/console.log)
   - Retornar códigos HTTP apropriados

7. **Validar Resultado**
   - Tentar iniciar a aplicação
   - Verificar se todos os endpoints respondem
   - Confirmar que não há erros de importação/sintaxe

8. **Imprimir Sumário**
   ```
   ================================
   PHASE 3: REFACTORING COMPLETE
   ================================
   ## New Project Structure
   src/
   ├── config/
   │   ├── settings.py
   │   └── database.py
   ├── models/
   │   ├── user.py
   │   └── ...
   ├── views/ (ou routes/)
   │   └── routes.py
   ├── controllers/
   │   ├── user_controller.py
   │   └── ...
   ├── middlewares/
   │   ├── auth.py
   │   └── error_handler.py
   └── app.py

   ## Validation
     ✓ Application boots without errors
     ✓ All endpoints respond correctly
     ✓ Configuration externalized
     ✓ Authentication implemented
     ✓ Zero critical anti-patterns remaining
   ================================
   ```

---

## Arquivos de Referência

Esta skill depende dos seguintes arquivos de conhecimento:

- **`project-analysis-heuristics.md`**: Como detectar linguagem, framework, banco de dados
- **`anti-patterns-catalog.md`**: Catálogo completo de anti-patterns com sinais de detecção
- **`audit-report-template.md`**: Template do relatório de auditoria
- **`mvc-guidelines.md`**: Regras do padrão MVC alvo
- **`refactoring-playbook.md`**: Padrões de transformação código antes/depois

---

## Notas Importantes

1. **Agnóstica de Tecnologia**: A skill deve funcionar com Python/Flask, Node.js/Express, e outras stacks
2. **Não Destrutiva**: Sempre pedir confirmação antes de modificar código (Fase 2 → Fase 3)
3. **Validação Obrigatória**: Sempre testar se a aplicação funciona após refatoração
4. **Priorização**: Focar em CRITICAL e HIGH primeiro
5. **Preservar Funcionalidade**: A refatoração não deve mudar o comportamento da aplicação
6. **Documentação**: Adicionar comentários explicando mudanças arquiteturais importantes

---

## Exemplos de Uso

### Projeto Python/Flask
```bash
cd code-smells-project
claude "/refactor-arch"
```

### Projeto Node.js/Express
```bash
cd ecommerce-api-legacy
claude "/refactor-arch"
```

A skill detectará automaticamente a stack e aplicará as transformações apropriadas.
