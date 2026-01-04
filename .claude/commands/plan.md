# Plan Command - Protocolo de Análise e Planejamento

## Objetivo
Investigar e diagnosticar problemas em workflows n8n usando n8n-MCP tools. **Análise apenas - SEM implementação de mudanças.** Cria arquivo de planejamento para ser usado pelo `/fix`.

## Diferença entre Comandos

| Comando | Ação | Escopo |
|---------|------|--------|
| `/plan` | Investigar e diagnosticar | **APENAS análise** - Lê workflow, cria arquivo de planejamento |
| `/fix` | Implementar correções | **Escrita** - Modifica workflow baseado no arquivo do `/plan` |

**Importante:** Este comando **NÃO** modifica o workflow. Apenas analisa e documenta o problema.

---

## Pré-requisitos

### 0. Verificação de Saúde do MCP
```javascript
n8n_health_check({mode: 'status'})
```

---

## Protocolo de Investigação

### 1. Identificar Workflow Alvo
**Caso usuário não fornecer workflow_id:**
- Ler variável `workflow_id_alvo` do arquivo `.env` (esse é o worfklow alvo que vc deve focar )

### 2. Obter Workflow Completo
```javascript
n8n_get_workflow({
  id: workflow_id_alvo,
  mode: 'full'  // JSON completo do workflow
})
```

### 3. Listar Execuções (Última Apenas)
```javascript
n8n_executions({
  action: 'list',
  workflowId: workflow_id_alvo,
  limit: 1,  // Apenas a última execução
  status: 'error'  // Opcional: filtrar por erro
})
```

### 4. Obter Detalhes da Execução
```javascript
n8n_executions({
  action: 'get',
  id: execution_id,  // ID da última execução
  mode: 'error',     // Otimizado para debugging de erros
  includeStackTrace: true,
  includeExecutionPath: true,
  fetchWorkflow: true,
  errorItemsLimit: 10  // Amostra de items upstream
})
```

### 5. Análise de Problemas
**Investigar:**
- Node específico que falhou
- Mensagens de erro
- Stack trace completo
- Input data do node upstream
- Caminho de execução até o erro

### 6. Obter Schema do Node (se necessário)
```javascript
get_node({
  nodeType: 'n8n-nodes-base.nodeType',
  detail: 'standard',  // Propriedades essenciais
  includeExamples: true
})
```

---

## Escopo e Restrições

### ⚠️ CRITICAL: Análise Apenas
- **NÃO implemente mudanças** no workflow
- **NÃO modifique** nodes ou conexões
- **NÃO execute** operações de escrita
- Apenas investigue, diagnostique e planeje

### Automação de Criação de Arquivo
- **Crie automaticamente** o arquivo de análise após concluir investigação
- **NÃO aguarde** confirmação do usuário
- Análise completa → arquivo criado → informe ao usuário

---

## Entrega

### Caminho Obrigatório do Arquivo
```
specs/[nome-do-problema].md
```

**Exemplo:** `specs/slack-webhook-timeout.md`

### Estrutura do Arquivo de Planejamento
1. **Resumo do Problema**
   - Workflow ID
   - Execution ID
   - Node com erro
   - Mensagem de erro

2. **Diagnóstico**
   - Causa raiz identificada
   - Contexto da execução
   - Data de entrada problemática

3. **Plano de Correção**
   - Passo a passo detalhado
   - Parâmetros a corrigir
   - Operações necessárias (updateNode, addConnection, etc.)
   - **Pronto para implementação via `/fix`**

4. **Validação Esperada**
   - Como verificar se a solução funcionou

---

## Restrições Críticas

### Execução Silenciosa
- Execute TODAS as tools em paralelo quando possível
- Sem comentários entre chamadas
- Responda APENAS após conclusão

### Ferramentas Permitidas (APENAS LEITURA)
**Investigação:**
- `n8n_health_check`
- `n8n_get_workflow`
- `n8n_executions`

**Análise:**
- `get_node`
- `validate_node`
- `n8n_validate_workflow`

### Diretório de Entrega
- Sempre salvar em `specs/`
- Nome descritivo do problema
- Extensão `.md` obrigatória
- Criação automática (sem confirmação)

---

## Modos de Execução Detalhada

### mode: 'error' (Recomendado para debugging)
```javascript
{
  action: 'get',
  id: execution_id,
  mode: 'error',
  errorItemsLimit: 10,      // Default: 2, Max: 100
  includeStackTrace: true,  // Default: false (truncado)
  includeExecutionPath: true, // Default: true
  fetchWorkflow: true       // Default: true
}
```

### mode: 'full'
- Todos os dados da execução
- Input + Output de todos os nodes
- Alto consumo de tokens

### mode: 'summary'
- 2 items por node
- Output data apenas
- Balanceado

### mode: 'preview'
- Estrutura da execução apenas
- Sem dados de items

---

## Padrão de Resposta

```
[Execução silenciosa das tools em paralelo]

## Análise Concluída

**Workflow:** {workflow_id}
**Execução:** {execution_id}
**Status:** {error|success|waiting}

### Problema Identificado
{descrição técnica}

### Causa Raiz
{análise detalhada}

### Plano de Correção
1. {passo 1}
2. {passo 2}
...

**Arquivo de planejamento criado:** `specs/{nome_problema}.md`

Próximo passo: Use `/fix {arquivo}` para aplicar as correções
```

---

## Integração com `/fix`

O comando `/plan` cria o arquivo de análise em `specs/`.
O comando `/fix` lê esse arquivo e implementa as correções.

**Fluxo completo:**
1. `/plan` → Investigar, diagnosticar, criar arquivo
2. `/fix specs/{arquivo}.md` → Implementar correções
