# Pipeline: n8n Workflow Modifier

## Overview
Workflow automatizado para diagnosticar e corrigir problemas em workflows n8n existentes. Integra os comandos `/plan` (análise) e `/fix` (correção) em uma pipeline sequencial que aceita workflow ID e descrição do problema via webhook.

**Requisito chave:** Variável no node Set para configurar workflow ID dinamicamente (sem depender de .env).

---

## Pipeline Structure

### Agent 1: workflow-analyzer
- **Purpose**: "Investigar workflow alvo e diagnosticar problemas"
- **Command**: `adw:analyze-workflow`
- **Inputs**:
  - `workflow_id`: ID do workflow a ser analisado
  - `problem_description`: Descrição do problema relatado
  - `working_directory`: Caminho do projeto Claude Code
- **Outputs**:
  - Arquivo de análise em `specs/[problem-name].md`
  - Diagnóstico completo (workflow ID, execution ID, node com erro, causa raiz)
  - Plano de correção detalhado
- **Prompt Focus**: **PLAN** (SDLC etapa de planejamento)
- **Dependencies**: Nenhuma (primeiro agente)

### Agent 2: workflow-fix-implementer
- **Purpose**: "Implementar correções baseado no arquivo de análise"
- **Command**: `adw:implement-fix`
- **Inputs**:
  - `analysis_file_path`: Caminho do arquivo gerado pelo Agent 1
  - `workflow_id`: ID do workflow alvo (repassado)
- **Outputs**:
  - Workflow modificado com correções aplicadas
  - Relatório de validação
  - Operações executadas (updateNode, addConnection, etc.)
- **Prompt Focus**: **BUILD** (SDLC etapa de implementação)
- **Dependencies**: Agent 1 (workflow-analyzer)

### Agent 3: fix-validator
- **Purpose**: "Validar correções e testar workflow modificado"
- **Command**: `adw:validate-fix`
- **Inputs**:
  - `workflow_id`: ID do workflow modificado
  - `validation_report`: Resultado da validação
- **Outputs**:
  - Relatório final de sucesso/erro
  - Teste de execução do workflow
  - Sugestões de rollback se necessário
- **Prompt Focus**: **TEST** (SDLC etapa de teste)
- **Dependencies**: Agent 2 (workflow-fix-implementer)

---

## Workflow Node Structure

### 1. Webhook (Trigger)
- **Type**: `n8n-nodes-base.webhook`
- **Path**: Auto-generado (ex: `workflow-modifier-webhook`)
- **Method**: POST
- **Payload esperado**:
  ```json
  {
    "workflow_id": "BVEJpyeRuGrNnruQ",
    "problem_description": "Webhook timeout após 30s",
    "working_directory": "C:\\.n8n_workflows"
  }
  ```

### 2. Set: config
- **Type**: `n8n-nodes-base.set`
- **Purpose**: Configurar variáveis globais da pipeline
- **Assignments**:
  - `working_directory`: Caminho do projeto (default: `C:\.n8n_workflows`)
  - `workflow_id`: ID do workflow alvo (**VARIÁVEL DINÂMICA** - vem do webhook)
  - `problem_description`: Descrição do problema (vem do webhook)
  - `command_agent1`: `/adw:analyze-workflow` (custom command)
  - `command_agent2`: `/adw:implement-fix` (custom command)
  - `command_agent3`: `/adw:validate-fix` (custom command)

### 3. Set: arguments
- **Type**: `n8n-nodes-base.set`
- **Purpose**: Preparar argumentos para o primeiro agente
- **Assignments**:
  - `arguments`: Concatenação de `workflow_id + " " + problem_description`
- **Path**: `arguments` (obrigatório para Claude Code funcionar)

### 4. Execute Command → adw:analyze-workflow
- **Type**: `n8n-nodes-base.executeCommand`
- **Command**:
  ```bash
  cd /d {{ $json.working_directory }} && echo. | claude -p "{{ $json.command_agent1 }} {{ $json.arguments }}" --dangerously-skip-permissions < NUL
  ```
- **Purpose**: Executar Agent 1 (análise)

### 5. Execute Command → adw:implement-fix
- **Type**: `n8n-nodes-base.executeCommand`
- **Command**:
  ```bash
  cd /d {{ $json.working_directory }} && echo. | claude -p "{{ $json.command_agent2 }} specs/{{ $json.analysis_file }}" --dangerously-skip-permissions < NUL
  ```
- **Purpose**: Executar Agent 2 (implementação)
- **Input**: Arquivo de análise gerado pelo Agent 1

### 6. Execute Command → adw:validate-fix
- **Type**: `n8n-nodes-base.executeCommand`
- **Command**:
  ```bash
  cd /d {{ $json.working_directory }} && echo. | claude -p "{{ $json.command_agent3 }} {{ $json.workflow_id }}" --dangerously-skip-permissions < NUL
  ```
- **Purpose**: Executar Agent 3 (validação)

### 7. Respond to Webhook (Optional)
- **Type**: `n8n-nodes-base.respondToWebhook`
- **Purpose**: Retornar resultado para o caller
- **Response**: Relatório final com status, correções aplicadas e validação

---

## Context Flow

```
[Webhook]
    ↓
[Set: config] → Define workflow_id (dinâmico), working_directory, commands
    ↓
[Set: arguments] → Prepara argumentos para Agent 1
    ↓
[Execute: adw:analyze-workflow]
    ↓ (produz specs/[problem].md)
[Execute: adw:implement-fix]
    ↓ (lê specs/[problem].md, modifica workflow)
[Execute: adw:validate-fix]
    ↓ (testa workflow modificado)
[Respond to Webhook] → Retorna relatório final
```

### Dados que fluem entre agentes:

**Agent 1 → Agent 2:**
- `specs/[problem-name].md` (arquivo de análise)
- Workflow ID (repassado)
- Diagnóstico detalhado

**Agent 2 → Agent 3:**
- Workflow ID (repassado)
- Lista de operações aplicadas
- Status da modificação

**Agent 3 → Saída:**
- Relatório final de validação
- Status de sucesso/erro
- Sugestões de próximo passo

---

## Success Criteria

- [ ] Webhook aceita workflow_id e problem_description dinamicamente
- [ ] Node Set permite configurar workflow_id sem .env (variável explicita)
- [ ] Agent 1 cria arquivo de análise em `specs/` automaticamente
- [ ] Agent 2 lê arquivo e aplica correções usando n8n_update_partial_workflow
- [ ] Agent 3 valida correções com n8n_validate_workflow
- [ ] Resposta final inclui status, operações executadas e validação
- [ ] Workflow segue template adw_template_v1.json (1 webhook, 2 sets, N execute commands)

---

## Technical Details

### Variável Dinâmica de Workflow ID

**No node "Set: config":**
```json
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "id": "workflow-id-var",
          "name": "workflow_id",
          "value": "={{ $json.workflow_id }}",
          "type": "string"
        },
        {
          "id": "working-dir-var",
          "name": "working_directory",
          "value": "C:\\.n8n_workflows",
          "type": "string"
        },
        {
          "id": "problem-desc-var",
          "name": "problem_description",
          "value": "={{ $json.problem_description }}",
          "type": "string"
        }
      ]
    }
  }
}
```

**Isso permite:**
- Webhook envia `workflow_id` no payload
- Não depende de variável de ambiente
- Reutilizável para qualquer workflow n8n

### Comandos Customizados Necessários

#### adw:analyze-workflow
Baseado em `plan.md`, mas adaptado para:
- Receber `workflow_id` e `problem_description` como $ARGUMENTS
- Criar arquivo automaticamente em `specs/`
- Retornar nome do arquivo criado

#### adw:implement-fix
Baseado em `fix.md`, mas adaptado para:
- Receber caminho do arquivo de análise como $ARGUMENTS
- Aplicar correções com n8n_update_partial_workflow
- Retornar operações executadas

#### adw:validate-fix
Novo comando para:
- Validar workflow modificado
- Testar execução se possível
- Gerar relatório final

---

## Next Steps

1. ✅ Plano criado
2. ⏭️ Criar custom commands (adw:2_create-commands)
3. ⏭️ Criar workflow no n8n (adw:3_create-workflow)
4. ⏭️ Testar pipeline completa

---

## Arquivos de Referência

- Template: `adw_template_v1.json`
- Command plan: `.claude/commands/plan.md`
- Command fix: `.claude/commands/fix.md`
- Diretório specs: `specs/` (será criado automaticamente)
