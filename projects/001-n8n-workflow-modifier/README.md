# n8n Workflow Modifier

## Descrição
Workflow automatizado para diagnosticar e corrigir problemas em workflows n8n existentes. Integra uma pipeline sequencial de 3 agentes especializados que aceita workflow ID e descrição do problema via webhook.

## Pipeline de Commands

1. **`/adw:analyze-workflow`** - Investigar workflow alvo e diagnosticar problemas
2. **`/adw:implement-fix`** - Implementar correções baseado na análise
3. **`/adw:validate-fix`** - Validar correções e testar workflow modificado

## Estrutura de Nodes (n8n)

```
[Webhook (POST)]
    ↓
[Set: config] → Define workflow_id, working_directory, commands
    ↓
[Set: arguments] → Prepara argumentos para Agent 1
    ↓
[Execute: adw:analyze-workflow] → Produz specs/[problem].md
    ↓
[Execute: adw:implement-fix] → Modifica workflow
    ↓
[Execute: adw:validate-fix] → Testa workflow
    ↓
[Respond to Webhook] → Retorna relatório final
```

## Contexto

### Variáveis Dinâmicas
- **workflow_id**: ID do workflow alvo (enviado via webhook)
- **problem_description**: Descrição do problema (enviado via webhook)
- **working_directory**: Diretório de trabalho (default: `C:\.n8n_workflows`)

### Fluxo de Dados
- **Agent 1 → Agent 2**: Arquivo de análise em `specs/[problem-name].md`
- **Agent 2 → Agent 3**: Workflow modificado e operações aplicadas
- **Agent 3 → Saída**: Relatório final de validação

### Arquivos Gerados
- `specs/[problem-name].md` - Análise detalhada do problema
- Relatórios de validação em cada etapa

## Workflow Details

**Nome:** n8n Workflow Modifier
**Workflow ID:** `jOxdXGt0wjBIJHWP`
**Localização:** `C:\.n8n_workflows\projects\001-n8n-workflow-modifier\workflow.json`
**Webhook Path:** `workflow-modifier-webhook`
**Método:** POST
**Status:** ✅ Criado e validado com sucesso

### Estrutura de Nodes
- Webhook (trigger)
- Set: config (variáveis globais)
- Set: arguments (prepara argumentos)
- Execute: adw:analyze-workflow (Agent 1)
- Execute: adw:implement-fix (Agent 2)
- Execute: adw:validate-fix (Agent 3)
- Respond to Webhook (resposta final)

### Validação
✅ Nodes válidos
✅ Connections válidas
✅ Expressões válidas
✅ Runtime profile OK

### Payload Esperado (Webhook)
```json
{
  "workflow_id": "BVEJpyeRuGrNnruQ",
  "problem_description": "Webhook timeout após 30s"
}
```

### Próximos Passos
1. **Importar workflow** no n8n usando o arquivo `workflow.json`
2. **Ativar o workflow** após importação
3. **Testar o webhook** com um payload de exemplo
4. **Verificar logs** de execução para validar cada step

## Criado em
2025-01-05
