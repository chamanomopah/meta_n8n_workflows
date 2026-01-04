# Fix Command - Protocolo de Correção

## Objetivo
Implementar correções do arquivo de análise e atualizar o workflow alvo. caso não for especificado o arquivo veja diretamente os specs na folder \specs\ e veja os disponiveis 

---

## Parâmetros
- `$ARGUMENTS`: Caminho do arquivo de análise gerado pelo `/plan`
  - Formato: `\specs\[nome_do_problema].md`
  - Exemplo: `\specs\slack-webhook-timeout.md`

---

## Fluxo de Correção

### 0. Verificação de Saúde do MCP
```javascript
n8n_health_check({mode: 'status'})
```

### 1. Ler Arquivo de Análise
- Ler `$ARGUMENTS` (arquivo gerado pelo `/plan`)
- Extrair:
  - Workflow ID
  - Node(s) a corrigir
  - Parâmetros problemáticos
  - Operações necessárias

### 2. Referência de Node (APENAS QUANDO NECESSÁRIO)
Use apenas se precisar adicionar novos nodes:

```javascript
get_node({
  nodeType: 'n8n-nodes-base.nodeType',
  detail: 'full',  // Schema completo (~3000-8000 tokens)
  includeExamples: true
})
```

### 3. Aplicar Correções
```javascript
n8n_update_partial_workflow({
  id: workflow_id_alvo,
  operations: [
    // Atualizar node existente
    {
      type: 'updateNode',
      nodeId: 'node-id',
      changes: {
        parameters: { /* config corrigida */ }
      }
    },
    // Adicionar novo node (quando necessário)
    {
      type: 'addNode',
      node: { /* config completa do node */ }
    },
    // Atualizar conexões
    {
      type: 'addConnection',
      source: 'node-id-string',      // 4 strings separadas
      target: 'target-node-id-string',
      sourcePort: 'main',
      targetPort: 'main'
    }
  ]
})
```

### 4. Validar Correções
```javascript
n8n_validate_workflow({
  id: workflow_id_alvo,
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true,
    profile: 'runtime'
  }
})
```

---

## Sintaxe Crítica de Operações

### addConnection (QUATRO strings separadas)
```javascript
{
  type: 'addConnection',
  source: 'node-id-string',      // String (não objeto)
  target: 'target-node-id-string',  // String
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

---

## Princípios de Correção

1. **Mudanças mínimas** - Modifique apenas o necessário
2. **Parâmetros explícitos** - Nunca confie em defaults
3. **Operações em lote** - Múltiplas mudanças em uma chamada
4. **Validação antes** - Use `validateOnly: true` para dry-run
5. **Teste após deploy** - Verifique execução do workflow

---

## Referência de Nodes Comuns

### Core Nodes (n8n-nodes-base.*)
1. **code** - JavaScript/Python scripting
2. **httpRequest** - Chamadas HTTP API
3. **webhook** - Triggers de eventos
4. **set** - Transformação de dados
5. **if** - Roteamento condicional
6. **manualTrigger** - Execução manual
7. **respondToWebhook** - Respostas de webhook
8. **scheduleTrigger** - Triggers baseados em tempo
9. **googleSheets** - Integração planilhas
10. **merge** - Mesclagem de dados
11. **switch** - Roteamento multi-branch
12. **telegram** - Integração Telegram
13. **splitInBatches** - Processamento em lotes
14. **openAi** - OpenAI (legado)
15. **gmail** - Automação email
16. **function** - Funções customizadas
17. **stickyNote** - Documentação workflow
18. **executeWorkflowTrigger** - Chamadas sub-workflow

### LangChain Nodes (@n8n/n8n-nodes-langchain.*)
- **agent** - AI agents
- **lmChatOpenAi** - OpenAI chat models

---

## Recuperação de Erros

Se validação falhar:

1. **Logs de execução**
   ```javascript
   n8n_executions({
     action: 'get',
     id: execution_id,
     mode: 'error'
   })
   ```

2. **Auto-fix (preview primeiro)**
   ```javascript
   n8n_autofix_workflow({
     id: workflow_id_alvo,
     applyFixes: false  // Preview antes de aplicar
   })
   ```

3. **Rollback se necessário**
   ```javascript
   n8n_workflow_versions({
     mode: 'rollback',
     workflowId: workflow_id_alvo,
     versionId: versao_anterior
   })
   ```

---

## Padrão de Resposta

```
[Execução silenciosa das tools]

## Correções Aplicadas

**Workflow:** {workflow_id}
**Arquivo de análise:** {argumentos}

### Mudanças Realizadas
- {node_1}: {descrição}
- {node_2}: {descrição}

### Validação
✅ Todas as validações passaram

### Operações Executadas
1. {tipo_operação} - {detalhes}
2. {tipo_operação} - {detalhes}
...
```
