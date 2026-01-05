---
description: Investigar workflow n8n e diagnosticar problemas usando comandos plan e diagnose
argument-hint: <workflow_id> <problem_description>
allowed-tools: Bash, Read, Write, Edit, Skill
---

# Analyze Workflow - Agente Especialista em Diagnóstico

## Contexto
Este agente especialista é responsável por investigar um workflow n8n existente, diagnosticar problemas e criar um plano detalhado de correção. Ele integra os comandos existentes `/plan` (análise) e `/diagnose` (diagnóstico completo) em um fluxo unificado.

## Inputs
- **$ARGUMENTS** (espaço separado):
  1. `workflow_id`: ID do workflow n8n a ser analisado
  2. `problem_description`: Descrição textual do problema relatado

- **Variáveis de ambiente** (via node Set no workflow):
  - `working_directory`: Diretório de trabalho (default: `C:\.n8n_workflows`)

## Task (One Purpose - SDLC PLAN)

Você deve executar as seguintes etapas sequencialmente:

### 1. Parse Arguments
Extrair `workflow_id` e `problem_description` de `$ARGUMENTS`:
- Primeiro token = workflow_id
- Restante dos tokens = problem_description

### 2. Executar Diagnóstico Completo
Usar o comando `/diagnose` para análise profunda:
```bash
/diagnose
```

**Foco do Diagnóstico:**
- Buscar workflows existentes no n8n
- Identificar o workflow alvo pelo ID
- Recuperar execuções recentes (últimas 10)
- Analisar execution path e errors
- Identificar node com falha
- Determinar causa raiz

### 3. Analisar Estrutura do Workflow
Usar ferramentas n8n-mcp para obter detalhes:
- `n8n_get_workflow` - estrutura completa
- `n8n_executions` - histórico de execuções
- Identificar nodes problemáticos
- Mapear conexões entre nodes

### 4. Criar Especificação de Correção
Gerar arquivo de análise em `specs/[problem-slug].md` com:

#### Frontmatter YAML
```yaml
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
analysis_date: "2025-01-05"
severity: "critical"
status: "diagnosed"
---
```

#### Seções do Documento

**1. Problema Diagnosticado**
- Descrição detalhada do problema
- Node específico que falha
- Mensagem de erro completa
- Execution ID que falhou

**2. Causa Raiz**
- Por que o problema ocorre
- Condições que disparam o erro
- Impacto no workflow

**3. Estrutura Atual**
- Lista de nodes do workflow
- Conexões problemáticas
- Configurações incorretas

**4. Plano de Correção**
Lista de operações necessárias usando `n8n_update_partial_workflow`:
- Operação 1: `updateNode` - corrigir parâmetro X
- Operação 2: `addConnection` - adicionar conexão Y
- Operação 3: `updateSettings` - modificar timeout
- [etc.]

**5. Validação Esperada**
- O que deve ser testado após correção
- Critérios de sucesso

### 5. Output Final
Imprimir no stdout:
```
✓ Analysis complete
File: specs/[problem-slug].md
Workflow: [workflow_id]
Diagnosis: [resumo do problema]
Operations required: [N]
```

**Foco SDLC**: PLAN - "O que estamos corrigindo e por quê?"

## Output

### Arquivo Criado
- **Caminho**: `specs/[problem-slug].md`
- **Conteúdo**: Diagnóstico completo + plano de correção detalhado

### Stdout
- Nome do arquivo criado
- Workflow ID analisado
- Resumo do diagnóstico
- Número de operações necessárias

## Validação

- [ ] Arguments parseados corretamente (workflow_id + problem_description)
- [ ] Comando `/diagnose` executado com sucesso
- [ ] Workflow alvo encontrado e acessado via n8n-mcp
- [ ] Execuções recentes analisadas
- [ ] Causa raiz identificada
- [ ] Arquivo de análise criado em `specs/`
- [ ] Arquivo contém frontmatter YAML válido
- [ ] Plano de correção com operações específicas (updateNode, addConnection, etc.)
- [ ] Stdout com caminho do arquivo para próximo agente

## Exemplo de Uso

**Input:**
```
$ARGUMENTS = "BVEJpyeRuGrNnruQ Webhook timeout após 30s durante processamento"
```

**Output:**
```
✓ Analysis complete
File: specs/webhook-timeout-after-30s.md
Workflow: BVEJpyeRuGrNnruQ
Diagnosis: Webhook node missing timeout configuration, default 30s insufficient
Operations required: 3 (updateNode, updateSettings, validate)
```

**Arquivo Gerado:** `specs/webhook-timeout-after-30s.md`
```markdown
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
analysis_date: "2025-01-05"
severity: "high"
status: "diagnosed"
---

## Problema Diagnosticado
Webhook node com timeout padrão de 30s está falhando...

## Causa Raiz
O node HTTP Request não tem timeout configurado...

## Plano de Correção
1. updateNode: adicionar timeout=120s ao webhook
2. updateSettings: executionTimeout=180000
3. validate: testar com payload pesado
```
