---
description: Cria workflow no n8n usando MCP baseado em template e plano (evita workflows mal formatados)
argument-hint: [plan-file]
allowed-tools: mcp__n8n__create_workflow, mcp__n8n__validate_workflow, mcp__n8n__get_node, Read, Write
model: claude-sonnet-4-5-20250929
---

# Criar Workflow n8n - Pipeline ADW

## Contexto
Você deve criar um workflow no n8n baseado no template `adw_template_v1.json` e no plano gerado pelo `/adw:plan-pipeline`.

**Arquivo de plano:** `$ARGUMENTS`
**Template:** `adw_template_v1.json`
**MCP Server:** n8n-mcp-tools

## Princípios Críticos (Baseado em fix.md)

### 1. Validação Antes de Criar
**NUNCA** crie um workflow sem validar primeiro. Workflows mal formatados não funcionam no n8n.

### 2. Uso Eficiente do MCP
- **Health check primeiro** → Verifique se MCP está responsivo
- **get_node apenas quando necessário** → Schema completo custa 3000-8000 tokens
- **validate sempre** → Use `validateOnly: true` para dry-run antes de aplicar

### 3. Sintaxe Crítica de Operações
- **addConnection** → QUATRO strings separadas (source, target, sourcePort, targetPort)
- **IF nodes** → Usar `branch: 'true'` ou `branch: 'false'`
- **Operações em lote** → Múltiplas mudanças em uma chamada

## Template de Referência (adw_template_v1.json)

Estrutura base que todos os workflows devem seguir:

```json
{
  "name": "ADW Template v1",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "adw-webhook",
        "responseMode": "responseNode"
      }
    },
    {
      "type": "n8n-nodes-base.set",
      "name": "Set Arguments",
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "arguments",
              "name": "arguments",
              "value": "={{ $json.body.arguments }}",
              "type": "string"
            }
          ]
        }
      }
    },
    {
      "type": "n8n-nodes-base.executeCommand",
      "name": "Execute Command 1",
      "parameters": {
        "command": "=/path/to/claude"
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Set Arguments", "type": "main", "index": 0}]]
    },
    "Set Arguments": {
      "main": [[{"node": "Execute Command 1", "type": "main", "index": 0}]]
    }
  }
}
```

## Fluxo de Execução

### 0. Health Check do MCP
```javascript
n8n_health_check({mode: 'status'})
```

Se falhar, **PARE** e reporte erro de conexão MCP.

### 1. Ler Plano e Template
```bash
Read `$ARGUMENTS`              # Plano da pipeline
Read `.n8n_workflows/adw_template_v1.json`  # Template base
Read `.n8n_workflows/projects/#[numero]-[nome]/README.md`  # Contexto
```

Extraia:
- Lista de commands/agents
- Estrutura de nodes necessária
- Ordem de execução

### 2. Referência de Nodes (APENAS QUANDO NECESSÁRIO)
Use **apenas** se precisar adicionar nodes que não existem no template:

```javascript
get_node({
  nodeType: 'n8n-nodes-base.nodeType',
  detail: 'full',  // Schema completo (~3000-8000 tokens)
  includeExamples: true
})
```

**Nodes mais comuns já conhecidos:**
- `n8n-nodes-base.webhook`
- `n8n-nodes-base.set`
- `n8n-nodes-base.executeCommand`
- `n8n-nodes-base.manualTrigger`
- `n8n-nodes-base.respondToWebhook`
- `n8n-nodes-base.code`
- `n8n-nodes-base.if`
- `n8n-nodes-base.merge`

### 3. Construir Estrutura do Workflow

Baseado no plano, construa:

**A) Nodes:**
```javascript
const nodes = [
  // 1. Webhook (trigger)
  {
    type: 'n8n-nodes-base.webhook',
    name: 'Webhook',
    parameters: {
      httpMethod: 'POST',
      path: '[nome-workflow]',
      responseMode: 'responseNode'
    }
  },

  // 2. Set Arguments (opcional - se workflow usar $ARGUMENTS)
  {
    type: 'n8n-nodes-base.set',
    name: 'Set Arguments',
    parameters: {
      assignments: {
        assignments: [
          {
            id: 'arguments',
            name: 'arguments',
            value: '={{ $json.body.arguments }}',
            type: 'string'
          }
        ]
      }
    }
  },

  // 3. Execute Commands (um para cada agent)
  {
    type: 'n8n-nodes-base.executeCommand',
    name: 'Execute [command-1]',
    parameters: {
      command: '=/path/to/claude /adw:[command-1]={{ $json.arguments }}'
    }
  },

  // ... mais Execute Commands conforme plano
];
```

**B) Connections (CRÍTICO - QUATRO strings separadas):**
```javascript
const connections = {
  'Webhook': {
    'main': [[{
      'node': 'Set Arguments',      // String (não objeto)
      'type': 'main',
      'index': 0
    }]]
  },
  'Set Arguments': {
    'main': [[{
      'node': 'Execute [command-1]', // String
      'type': 'main',
      'index': 0
    }]]
  },
  'Execute [command-1]': {
    'main': [[{
      'node': 'Execute [command-2]', // String
      'type': 'main',
      'index': 0
    }]]
  }
  // ... continue conectando todos os Execute Commands em sequência
};
```

### 4. Criar Workflow com Validação (Dry-Run Primeiro)

```javascript
n8n_create_workflow({
  name: '[nome-do-workflow]',
  nodes: nodes,
  connections: connections,
  options: {
    validateOnly: true  // DRY-RUN - não salva ainda
  }
})
```

### 5. Analisar Resultado da Validação

Se validation retornar erros:
```javascript
// Ver erros específicos
{
  "errors": [
    {
      "node": "Execute Command 1",
      "message": "Invalid parameter: command"
    }
  ]
}
```

**Corrija os erros antes de prosseguir.**

### 6. Criar Workflow Definitivamente

Após validação passar:

```javascript
n8n_create_workflow({
  name: '[nome-do-workflow]',
  nodes: nodes,
  connections: connections,
  options: {
    validateOnly: false  // AGORA salva
  }
})
```

### 7. Salvar workflow.json no Projeto
```javascript
Write(
  'C:\.n8n_workflows\projects\#[numero]-[nome]\workflow.json',
  JSON.stringify({name, nodes, connections}, null, 2)
)
```

## Sintaxe Crítica de Conexões

### Conexão Padrão (QUATRO strings)
```javascript
{
  type: 'addConnection',
  source: 'node-id-string',          // String (não objeto)
  target: 'target-node-id-string',   // String
  sourcePort: 'main',
  targetPort: 'main'
}
```

### IF Node - Multi-Output Routing
```javascript
// Branch TRUE (condição atendida)
{
  type: 'addConnection',
  source: 'if-node-id',
  target: 'success-handler-id',
  sourcePort: 'main',
  targetPort: 'main',
  branch: 'true'  // Obrigatório para IF nodes
}

// Branch FALSE (condição NÃO atendida)
{
  type: 'addConnection',
  source: 'if-node-id',
  target: 'failure-handler-id',
  sourcePort: 'main',
  targetPort: 'main',
  branch: 'false'
}
```

## Validação Pós-Criação

### 1. Validar Workflow Criado
```javascript
n8n_validate_workflow({
  id: workflow_id_criado,
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true,
    profile: 'runtime'
  }
})
```

### 2. Testar Execução (Opcional)
```javascript
n8n_execute_workflow({
  id: workflow_id_criado,
  data: {
    arguments: 'test-arguments'
  }
})
```

## Princípios de Correção (baseado em fix.md)

1. **Mudanças mínimas** - Modifique apenas o necessário
2. **Parâmetros explícitos** - Nunca confie em defaults
3. **Operações em lote** - Múltiplas mudanças em uma chamada
4. **Validação antes** - Use `validateOnly: true` para dry-run
5. **Teste após deploy** - Verifique execução do workflow

## Recuperação de Erros

Se validação ou criação falhar:

### 1. Logs de Execução
```javascript
n8n_executions({
  action: 'get',
  id: execution_id,
  mode: 'error'
})
```

### 2. Auto-Fix (Preview Primeiro)
```javascript
n8n_autofix_workflow({
  id: workflow_id,
  applyFixes: false  // Preview antes de aplicar
})
```

### 3. Rollback se Necessário
```javascript
n8n_workflow_versions({
  mode: 'rollback',
  workflowId: workflow_id,
  versionId: versao_anterior
})
```

## Padrão de Resposta

```
## Workflow Criado com Sucesso

**Nome:** [nome-do-workflow]
**Workflow ID:** [id]
**Localização:** `C:\.n8n_workflows\projects\#[numero]-[nome]\workflow.json`

### Estrutura de Nodes
- Webhook (trigger)
- Set Arguments (opcional)
- Execute Command → /adw:[command-1]
- Execute Command → /adw:[command-2]
[...]

### Validação
✅ Nodes válidos
✅ Connections válidas
✅ Expressões válidas
✅ Runtime profile OK

### Próximos Passos
1. Teste o workflow via webhook
2. Execute manualmente para validar cada step
3. Verifique logs de execução
```

## Checklist de Conclusão

- [ ] Health check do MCP passou
- [ ] Plano lido e compreendido
- [ ] Estrutura de nodes baseada em template
- [ ] Connections com QUATRO strings separadas
- [ ] Validação dry-run passou
- [ ] Workflow criado no n8n
- [ ] workflow.json salvo no projeto
- [ ] Validação pós-criação OK
- [ ] README atualizado com workflow ID

## Anti-Patterns

❌ **NÃO FAZER:**
- Criar workflow SEM validar primeiro
- Usar objetos em vez de strings em connections
- Esquecer do `branch` em IF nodes
- Criar workflow sem health check do MCP
- Pular validação pós-criação

✅ **FAZER:**
- Sempre `validateOnly: true` primeiro
- Seguir sintaxe de QUATRO strings
- Health check antes de tudo
- Testar execução após criação
- Salvar workflow.json no projeto
