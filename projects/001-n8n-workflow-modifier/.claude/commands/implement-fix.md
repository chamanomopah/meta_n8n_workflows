---
description: Implementar correções no workflow n8n baseado no arquivo de análise
argument-hint: <analysis_file_path>
allowed-tools: Bash, Read, Write, Edit, mcp__n8n-mcp__n8n_update_partial_workflow
---

# Implement Fix - Agente Especialista em Correção

## Contexto
Este agente especialista é responsável por ler o arquivo de análise gerado pelo Agent 1 e aplicar as correções necessárias no workflow n8n usando a API `n8n_update_partial_workflow`. Ele deve executar cada operação planejada de forma segura e validar após cada mudança.

## Inputs
- **$ARGUMENTS**:
  - `analysis_file_path`: Caminho completo para o arquivo de análise (ex: `specs/webhook-timeout.md`)

- **Arquivo de Análise** (lido do disco):
  - Deve conter frontmatter YAML com `workflow_id`
  - Deve ter seção "Plano de Correção" com operações detalhadas

## Task (One Purpose - SDLC BUILD)

Você deve executar as seguintes etapas sequencialmente:

### 1. Parse Arguments
Extrair `analysis_file_path` de `$ARGUMENTS`:
- Único argumento = caminho do arquivo de análise

### 2. Ler Arquivo de Análise
Usar `Read` para carregar o arquivo:
- Extrair `workflow_id` do frontmatter YAML
- Extrair lista de operações da seção "Plano de Correção"
- Identificar severity e status

### 3. Validar Pré-requisitos
Antes de aplicar qualquer correção:
- [ ] Workflow ID existe no frontmatter
- [ ] Plano de correção está presente
- [ ] Operações estão bem definidas (tipo, alvo, parâmetros)
- [ ] Workflow está acessível via n8n-mcp

Se algum pré-requisito falhar, reportar erro e parar.

### 4. Aplicar Correções Sequencialmente
Para cada operação do plano, executar em ordem:

#### Operação: updateNode
```python
# Exemplo de chamada MCP
mcp__n8n-mcp__n8n_update_partial_workflow(
  id=workflow_id,
  operations=[
    {
      "type": "updateNode",
      "nodeName": "Nome do Node",
      "updates": {
        "parameters": {
          "timeout": 120000
        }
      }
    }
  ]
)
```

#### Operação: addConnection
```python
mcp__n8n-mcp__n8n_update_partial_workflow(
  id=workflow_id,
  operations=[
    {
      "type": "addConnection",
      "sourceNode": "Node A",
      "targetNode": "Node B",
      "sourceOutput": 0,
      "targetInput": 0
    }
  ]
)
```

#### Operação: removeConnection
```python
mcp__n8n-mcp__n8n_update_partial_workflow(
  id=workflow_id,
  operations=[
    {
      "type": "removeConnection",
      "sourceNode": "Node A",
      "targetNode": "Node B",
      "sourceOutput": 0,
      "targetInput": 0
    }
  ]
)
```

#### Operação: updateSettings
```python
mcp__n8n-mcp__n8n_update_partial_workflow(
  id=workflow_id,
  operations=[
    {
      "type": "updateSettings",
      "settings": {
        "executionTimeout": 180000
      }
    }
  ]
)
```

#### Operação: moveNode
```python
mcp__n8n-mcp__n8n_update_partial_workflow(
  id=workflow_id,
  operations=[
    {
      "type": "moveNode",
      "nodeName": "Node A",
      "position": [250, 300]
    }
  ]
)
```

### 5. Tratamento de Erros
Se uma operação falhar:
- Logar operação que falhou + erro completo
- Parar execução (não aplicar operações restantes)
- Sugerir rollback manual
- Reportar status partial

### 6. Criar Relatório de Implementação
Gerar arquivo `specs/[problem-name]-implementation.md` com:

#### Frontmatter
```yaml
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
implementation_date: "2025-01-05"
status: "completed" | "partial" | "failed"
operations_applied: 3
operations_failed: 0
---
```

#### Conteúdo
**Operações Aplicadas:**
- [✓] Operação 1: updateNode - Webhook timeout
  - Parâmetros alterados: timeout=120000
  - Status: Success

- [✓] Operação 2: updateSettings - Execution timeout
  - Parâmetros alterados: executionTimeout=180000
  - Status: Success

**Resumo de Mudanças:**
- Nodes modificados: 2
- Conexões adicionadas: 0
- Settings alterados: 1

**Próximos Passos:**
- Executar `/adw:validate-fix <workflow_id>`
- Testar workflow com webhook real

### 7. Output Final
Imprimir no stdout:
```
✓ Implementation complete
File: specs/[problem-name]-implementation.md
Workflow: [workflow_id]
Operations: [N] applied, [0] failed
Status: [completed|partial|failed]
Next: /adw:validate-fix [workflow_id]
```

**Foco SDLC**: BUILD - "Fizemos as mudanças acontecerem?"

## Output

### Arquivo Criado
- **Caminho**: `specs/[problem-name]-implementation.md`
- **Conteúdo**: Relatório detalhado de operações aplicadas

### Stdout
- Nome do arquivo de implementação
- Workflow ID modificado
- Contagem de operações aplicadas/falhadas
- Status final
- Próximo comando a executar

## Validação

- [ ] Argumento (analysis_file_path) parseado corretamente
- [ ] Arquivo de análise lido com sucesso
- [ ] Frontmatter YAML válido com workflow_id
- [ ] Plano de correção extraído corretamente
- [ ] Operações aplicadas sequencialmente
- [ ] Cada operação validada antes da próxima
- [ ] Erros tratados com logging adequado
- [ ] Relatório de implementação criado
- [ ] Stdout contém caminho do relatório e status

## Exemplo de Uso

**Input:**
```
$ARGUMENTS = "specs/webhook-timeout.md"
```

**Arquivo de Análise:** `specs/webhook-timeout.md`
```markdown
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
status: "diagnosed"
---

## Plano de Correção
1. updateNode: adicionar timeout=120s ao webhook
2. updateSettings: executionTimeout=180000
```

**Output:**
```
✓ Implementation complete
File: specs/webhook-timeout-implementation.md
Workflow: BVEJpyeRuGrNnruQ
Operations: 2 applied, 0 failed
Status: completed
Next: /adw:validate-fix BVEJpyeRuGrNnruQ
```

**Arquivo Gerado:** `specs/webhook-timeout-implementation.md`
```markdown
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
status: "completed"
operations_applied: 2
---

## Operações Aplicadas
- [✓] updateNode - Webhook timeout
- [✓] updateSettings - Execution timeout
```
