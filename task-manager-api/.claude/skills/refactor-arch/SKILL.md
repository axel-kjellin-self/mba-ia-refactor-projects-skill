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

4. **Salvar o Relatório em `reports/`** — entregável obrigatório

   Imprimir no chat **não basta**: o relatório precisa ficar versionado no repositório.

   - Caminho: `<raiz-do-repositório>/reports/audit-project-<N>.md`
   - Numeração fixa: `1` = code-smells-project · `2` = ecommerce-api-legacy ·
     `3` = task-manager-api
   - ⚠️ A skill roda de **dentro** do projeto; `reports/` fica um nível **acima**.
     Confirme a raiz antes de escrever (ex.: `git rev-parse --show-toplevel`).
   - Crie o diretório se não existir.
   - Se o arquivo já existir, **sobrescreva**: vale sempre a execução mais recente.
     Um relatório antigo apontando arquivos que já não existem é pior que nenhum.
   - O conteúdo salvo deve ser **idêntico** ao impresso — mesmos findings, mesmas
     linhas, mesma contagem.

5. **Exibir Relatório e Pausar**
   - Imprima o relatório completo
   - Informe onde ele foi salvo
   - **IMPORTANTE**: Pergunte ao usuário se deseja prosseguir para Fase 3
   - Aguarde confirmação explícita (y/n) antes de modificar qualquer arquivo

   ```
   Phase 2 complete. Report saved to reports/audit-project-<N>.md
   Proceed with refactoring (Phase 3)? [y/n]
   ```

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
   - **HIGH: Missing Auth** → Criar middleware **e aplicá-lo em cada rota** (ver 3.1)
   - **HIGH: N+1 Queries** → Otimizar com JOINs ou eager loading
   - **MEDIUM: Missing Validation** → Adicionar schema validation
   - **LOW: Magic Numbers** → Extrair para constantes

   ### 3.1 Autenticação: criar o middleware NÃO é suficiente

   ⚠️ Criar `middlewares/auth.py` e importá-lo no arquivo de rotas **não protege nada**.
   Um decorator importado e não aplicado é código morto — o endpoint continua público.

   Para **cada rota** do projeto, decida e aplique explicitamente uma política:

   | Política | Quando usar |
   |----------|-------------|
   | pública | login, cadastro, catálogo de leitura, health check |
   | `require_auth` | qualquer endpoint que dependa de um usuário logado |
   | `require_owner_or_admin` | rota com id de usuário no path (`/users/<id>`) |
   | `require_admin` | listagens globais, relatórios, escrita em dados de catálogo |

   Aplicação, por estilo de registro de rota:

   ```python
   # Flask com decorator
   @bp.route('/tasks', methods=['GET'])
   @require_auth
   def listar(): ...

   # Flask registrando controller (envolva a função!)
   bp.route('/tasks', methods=['GET'])(require_auth(controller.listar))
   ```

   ```javascript
   // Express: por rota, ou no router inteiro
   router.get('/:id', requireAuth, asyncHandler(ctrl.get));
   router.use(requireAuth); router.use(requireRole('admin'));
   ```

   **Nenhuma rota pode ficar sem decisão registrada.** Se for pública, diga por quê
   em comentário. Comentários como `# should be protected in production` são proibidos:
   ou protege agora, ou justifica por que é pública.

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

7. **Eliminar o Código Legado**

   ⚠️ Criar `src/` sem apagar o código antigo **não resolve os findings** — apenas
   duplica o projeto. Todo finding CRITICAL continua vivo enquanto o arquivo original
   existir, mesmo que nada o importe: o avaliador (e um `grep`) ainda o encontram.

   - **Delete** os arquivos/pastas substituídos pela nova estrutura. O histórico do
     git preserva o original; não é preciso manter cópia na árvore de trabalho.
   - **Não** mova para `legacy/`, `old/` ou `_backup/`. Isso não elimina o finding,
     só o esconde de leitores desatentos.
   - **Reaponte os scripts auxiliares** (`seed.py`, `manage.py`, fixtures, migrations)
     para os novos módulos. Eles não aparecem nas rotas e passam despercebidos.
   - Confirme que nada sobrou:
     ```bash
     grep -rn "hashlib.md5\|sha1(" --include=*.py --include=*.js . | grep -v node_modules
     grep -rn "^from models\|^from routes\|require('../AppManager')" .
     ```
     Exemplos dentro dos arquivos de referência da própria skill são esperados;
     qualquer ocorrência em código do projeto é falha.

8. **Validar Resultado**

   Execute os comandos e **cole a saída real**. Não marque um item sem tê-lo rodado.

   ```bash
   # a) a aplicação sobe?
   python app.py    # ou: npm start
   # b) endpoint público responde?
   curl -s -o /dev/null -w "%{http_code}" http://localhost:<porta>/health
   # c) endpoint protegido REJEITA sem token? (401/403 = sucesso)
   curl -s -o /dev/null -w "%{http_code}" http://localhost:<porta>/<rota-protegida>
   # d) endpoint protegido ACEITA com token?
   curl -s -o /dev/null -w "%{http_code}" http://localhost:<porta>/<rota-protegida> \
     -H "Authorization: Bearer <token>"
   ```

   Se não for possível executar (dependências ausentes, sem rede), **diga isso
   explicitamente** no sumário em vez de presumir sucesso.

   Verificação estática obrigatória — todo decorator importado é usado?
   ```bash
   grep -rn "require_auth\|require_admin\|requireAuth" src/routes/
   ```
   Se um nome aparece só na linha de `import`, a rota está desprotegida. Volte ao 3.1.

9. **Imprimir Sumário**

   ⚠️ O bloco abaixo é um **formulário a preencher**, não texto para copiar. Cada
   linha de `## Validation` só recebe `✓` se o comando do passo 8 foi executado e
   passou. Use `✗` para o que falhou e `?` para o que não foi possível verificar,
   sempre com a razão ao lado. Um sumário todo `✓` sem execução é relatório falso —
   é pior que uma refatoração incompleta, porque esconde o que ficou por fazer.

   Nas contagens, use os números do relatório da Fase 2 deste projeto. Não invente
   métricas de performance ("99% de redução", "score 10/10") que não foram medidas;
   se for estimativa, escreva "estimado".

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

   ## Validation      [✓ verificado | ✗ falhou | ? não verificável]
     <?> Application boots without errors      <cole a saída ou a razão>
     <?> Public endpoint responds              <código HTTP observado>
     <?> Protected endpoint rejects w/o token  <código HTTP observado>
     <?> Protected endpoint accepts w/ token   <código HTTP observado>
     <?> Configuration externalized            <nenhum secret no código?>
     <?> Every imported decorator is applied   <saída do grep do passo 8>
     <?> Legacy code deleted                   <saída do grep do passo 7>

   ## Findings resolvidos (da Fase 2)
     CRITICAL: <n>/<total>   HIGH: <n>/<total>
     MEDIUM:   <n>/<total>   LOW:  <n>/<total>
     Pendentes: <liste o que ficou e por quê, ou "nenhum">
   ================================
   ```

10. **Registrar a Comprovação no README do Repositório**

    O relatório da Fase 2 prova o que estava **errado**. O README precisa provar o que
    ficou **certo** — é a evidência de conclusão. Sem isso, a única prova de que a
    aplicação roda depois da refatoração é a palavra do agente.

    Na raiz do repositório, atualize o `README.md` acrescentando, para este projeto:

    - **Antes/depois da estrutura** de diretórios
    - **Checklist de validação preenchido**, específico deste projeto (não um genérico
      compartilhado entre os três)
    - **Logs reais** da aplicação rodando após a refatoração: saída do boot e os
      códigos HTTP observados nos `curl` do passo 8, copiados literalmente
    - **Contagem de findings** por severidade, igual à do relatório da Fase 2
    - **Link** para `reports/audit-project-<N>.md`

    Regras:
    - Números no README **devem bater** com os do relatório salvo. Se divergirem, o
      relatório é a fonte da verdade — corrija o README, não o relatório.
    - Não descreva como resolvido o que ficou pendente; liste o pendente.
    - Preserve as seções já existentes de outros projetos: **acrescente, não substitua**.

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
