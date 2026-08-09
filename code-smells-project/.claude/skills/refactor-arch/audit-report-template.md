# Audit Report Template

Use este template para gerar relatórios de auditoria estruturados na Fase 2.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework>
Files:   <número> analyzed | ~<número> lines of code

## Summary
CRITICAL: <count> | HIGH: <count> | MEDIUM: <count> | LOW: <count>

## Findings

### [CRITICAL] <Título do Problema>
File: <caminho/arquivo.ext>:<linha-inicial>-<linha-final>
Description: <Descrição clara do que está errado>
Impact: <Por que isso é crítico>
Recommendation: <Como corrigir>

Code:
```<linguagem>
<trecho de código problemático>
```

---

### [HIGH] <Título do Problema>
File: <caminho/arquivo.ext>:<linha>
Description: <Descrição>
Impact: <Impacto>
Recommendation: <Recomendação>

---

### [MEDIUM] <Título do Problema>
File: <caminho/arquivo.ext>:<linha>
Description: <Descrição>
Impact: <Impacto>
Recommendation: <Recomendação>

---

### [LOW] <Título do Problema>
File: <caminho/arquivo.ext>:<linha>
Description: <Descrição>
Impact: <Impacto>
Recommendation: <Recomendação>

---

================================
Total: <número-total> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Instruções de Uso

### 1. Header do Relatório

Preencha com informações detectadas na Fase 1:
- **Project**: Nome do diretório do projeto
- **Stack**: Linguagem + Framework (ex: "Python + Flask 3.1.1")
- **Files**: Número de arquivos analisados e estimativa de linhas de código

### 2. Summary

Conte o número de findings por severidade:
```
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 2
```

### 3. Findings

**IMPORTANTE**: Liste TODOS os findings encontrados, ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW).

Para cada finding, inclua:

#### Título
- Use formato: `[SEVERIDADE] Nome Descritivo do Problema`
- Exemplos:
  - `[CRITICAL] SQL Injection in User Login`
  - `[HIGH] God Class - All Logic in Single File`
  - `[MEDIUM] N+1 Query Problem in Order Listing`
  - `[LOW] Magic Numbers in Discount Calculation`

#### File e Linhas
- **SEMPRE** inclua arquivo e linhas EXATAS
- Formatos aceitos:
  - Linha única: `app.py:47`
  - Range de linhas: `models.py:28-45`
  - Múltiplas localizações: `models.py:28, 48-49, 57-60`
- Use caminhos relativos ao root do projeto

#### Description
- Explique claramente o que está errado
- Seja específico, não genérico
- Exemplo RUIM: "Código com problemas"
- Exemplo BOM: "Queries SQL construídas com concatenação de strings ao invés de queries parametrizadas"

#### Impact
- Explique POR QUE isso é um problema
- Qual o risco ou consequência?
- Exemplos:
  - "Permite ataques de SQL injection, comprometendo todo o banco de dados"
  - "Impossível testar em isolamento, qualquer mudança afeta tudo"
  - "Performance degradada em escala, 100 pedidos = 300+ queries"

#### Recommendation
- Como corrigir o problema
- Seja acionável e específico
- Exemplos:
  - "Usar queries parametrizadas: `cursor.execute('SELECT * WHERE id = ?', (id,))`"
  - "Separar em camadas: Models (dados) + Services (lógica) + Controllers (HTTP)"
  - "Usar JOINs: `SELECT * FROM orders JOIN items ON orders.id = items.order_id`"

#### Code (Opcional)
- Inclua trecho de código problemático quando ajudar a ilustrar
- Use syntax highlighting correto
- Limite a ~10 linhas para clareza

### 4. Ordenação

**Ordem obrigatória**:
1. CRITICAL (mais urgente primeiro)
2. HIGH
3. MEDIUM
4. LOW

Dentro de cada severidade, ordene por:
1. Segurança (SQL injection, secrets, auth) primeiro
2. Arquitetura (God Class, coupling)
3. Performance (N+1 queries)
4. Qualidade (naming, docs)

### 5. Total e Confirmação

No final:
```
================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**IMPORTANTE**: Sempre pergunte ao usuário se deseja prosseguir para Fase 3. **NÃO MODIFICAR NENHUM ARQUIVO** sem confirmação explícita.

---

## Exemplo Completo de Finding

```markdown
### [CRITICAL] SQL Injection in Multiple Endpoints

File: models.py:28, 48-49, 57-60, 68, 92, 109-110
Description: Múltiplas funções constroem queries SQL usando concatenação de strings ao invés de queries parametrizadas. Isso permite que atacantes injetem código SQL arbitrário.

Examples:
- `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` (linha 28)
- `cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")` (linha 109-110)

Attack Vectors:
- Login bypass: `email = "admin' --"`
- Data extraction: `id = "1 OR 1=1"`
- Database destruction: `id = "1; DROP TABLE usuarios; --"`

Impact: Comprometimento completo do banco de dados. Atacantes podem roubar, modificar ou deletar todos os dados. Acesso não autorizado a todas as contas de usuário.

Recommendation: Substituir TODAS as queries por queries parametrizadas:
```python
# ANTES (vulnerável)
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

# DEPOIS (seguro)
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

OU migrar para ORM (SQLAlchemy):
```python
produto = Produto.query.get(id)
```
```

---

## Template para Copy-Paste

```markdown
### [SEVERIDADE] <Título>
File: <arquivo>:<linhas>
Description: <Descrição detalhada>
Impact: <Impacto e consequências>
Recommendation: <Como corrigir>

---
```

---

## Boas Práticas

1. **Seja Específico**: Linhas exatas, não aproximações
2. **Seja Claro**: Explique para alguém que não conhece o código
3. **Seja Acionável**: Recomendações devem ser implementáveis
4. **Agrupe Similaridades**: Se mesmo problema aparece 10+ vezes, agrupe em um finding
5. **Priorize Corretamente**: CRITICAL = bloqueia deploy, HIGH = fix antes de prod
6. **Inclua Código**: Quando ajudar a ilustrar o problema
7. **Mencione Compliance**: PCI-DSS, OWASP, GDPR quando relevante
8. **Quantifique Performance**: "100 pedidos = 300+ queries" é melhor que "lento"

---

## Classificação de Severidade (Referência Rápida)

### CRITICAL
- SQL Injection
- Hardcoded credentials/secrets
- Weak/broken cryptography
- Plaintext passwords
- Exposed secrets in API
- Dangerous endpoints sem auth (reset-db, arbitrary query)

### HIGH
- Missing authentication/authorization
- God Class / God Method
- N+1 Query Problem
- Business logic in controllers
- Callback Hell (Node.js)
- Tight coupling
- Improper error handling (bare except)

### MEDIUM
- Code duplication
- Missing input validation
- Race conditions / missing transactions
- Missing database constraints
- Debug mode in production
- Weak password requirements
- Deprecated API usage
- LIKE injection

### LOW
- Magic numbers
- Poor variable naming
- Missing documentation/type hints
- Unused/dead code
- Inadequate HTTP status codes
