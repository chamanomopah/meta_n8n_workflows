---
description: Planeja pipeline de commands para workflows n8n baseado em agentes especializados (One Agent, One Prompt, One Purpose)
argument-hint: [workflow-name]
allowed-tools: Read, Write, Glob, Grep
model: claude-sonnet-4-5-20250929
---

# Planejamento de Pipeline ADW - Agent Developer Workflow

## Contexto
Baseado no princípio **"One Agent, One Prompt, One Purpose"** (Tactic #6), você precisa planejar uma pipeline de slash commands especializados para automatizar a criação de workflows no n8n.

**Workflow solicitado:** `$ARGUMENTS`

## Template de Referência
Todos os workflows devem seguir a estrutura base do `adw_template_v1.json`:
- 1 node Webhook (trigger)
- 1-2 nodes Set (depende se precisa de $arguments)
- N nodes Execute Command (um para cada custom command/agente especializado)

## Princípios Fundamentais

### 1. Agentes Especializados
Cada **custom command** = 1 **Claude Code agent** especializado com:
- **Único propósito** focado e específico
- **Prompt dedicado** para uma tarefa bem definida
- **Contexto mínimo** necessário para executar bem
- **Reprodutibilidade** e capacidade de commit/melhoria

### 2. SDLC como Perguntas e Respostas
Mapeie cada etapa do ciclo de vida do desenvolvimento:
- **Plan** → "O que estamos construindo?"
- **Build** → "Fizemos acontecer?"
- **Test** → "Funciona?"
- **Review** → "É o que planejamos?"
- **Document** → "Como funciona?"

### 3. Evite Context Pollution
- **Contexto mínimo** para resolver o problema
- **Specialized agents** liberam a context window
- **Foco no que importa**: a tarefa original
- **Overhead de contexto** = Performance reduzida

## Sua Tarefa

### 1. Analisar o Workflow Solicitado
Entenda qual funcionalidade o workflow `$ARGUMENTS` deve implementar.

### 2. Decompor em Agentes Especializados
Divida o workflow em **passos sequenciais**, onde cada passo será:
- **1 agent especializado** (1 custom command)
- **1 prompt focado** (1 propósito específico)
- **1 parte do todo** (não tente fazer tudo em um agent)

**Pergunta-chave**: "Quais são as etapas lógicas sequenciais para construir este workflow?"

### 3. Mapear para Pipeline de Commands
Para cada agente, defina:
```yaml
- agent_name: nome-do-agente
  purpose: "O que este agente faz em UMA frase"
  prompt_type: plan | build | test | review | document
  inputs: ["o que precisa receber"]
  outputs: ["o que produz"]
  dependencies: ["quais agentes precisam rodar antes"]
```

### 4. Criar Arquivo de Plano
Salve o plano em: `.n8n_workflows/plans/[nome-do-workflow]-plan.md`

**Template do plano:**
```markdown
# Pipeline: [Nome do Workflow]

## Overview
[Descrição em 2-3 linhas do objetivo do workflow]

## Pipeline Structure

### Agent 1: [nome-do-agente-1]
- **Purpose**: [único propósito]
- **Command**: `adw:[nome-do-command-1]`
- **Inputs**: [o que recebe]
- **Outputs**: [o que produz]
- **Prompt Focus**: [qual etapa do SDLC]

### Agent 2: [nome-do-agente-2]
- **Purpose**: [único propósito]
- **Command**: `adw:[nome-do-command-2]`
- **Inputs**: [saídas do Agent 1]
- **Outputs**: [o que produz]
- **Prompt Focus**: [qual etapa do SDLC]

[... continue para todos os agentes]

## Workflow Node Structure
1. Webhook (trigger)
2. Set $arguments (se necessário)
3. Execute Command → adw:[command-do-agent-1]
4. Execute Command → adw:[command-do-agent-2]
[... continue]

## Context Flow
[Descreva como dados/artequatos fluem entre agentes]

## Success Criteria
- [ ] Critério 1
- [ ] Critério 2
```

## Padrões de Decomposição

### Exemplo 1: Workflow de Integração Slack
```yaml
Agent 1 (plan):
  purpose: "Analisar requisitos e criar plano de implementação"
  output: "specs/slack-integration.md"

Agent 2 (build):
  purpose: "Criar estrutura base do workflow no n8n"
  input: "specs/slack-integration.md"
  output: "workflow.json + commands/"

Agent 3 (test):
  purpose: "Validar estrutura e sintaxe do workflow criado"
  input: "workflow.json"
  output: "validation-report.md"

Agent 4 (review):
  purpose: "Revisar se workflow atende ao plano original"
  input: "specs/slack-integration.md + workflow.json"
  output: "review-report.md"
```

### Exemplo 2: Workflow de Automação de Email
```yaml
Agent 1 (plan): "Especificar fluxo de autenticação e envio"
Agent 2 (build): "Criar nodes HTTP Request e Set"
Agent 3 (test): "Testar endpoints e autenticação"
Agent 4 (document): "Gerar README com instruções de uso"
```

## Constraints & Validações

### Regras de Ouro
1. **Um agente = Um propósito** (não sobrecarregue)
2. **Pipeline sequencial** (Agent 2 depende do Agent 1)
3. **MVP primeiro** (comece com mínimo de agentes)
4. **Contexto limpo** (cada agent recebe apenas o necessário)
5. **Validação contínua** (test e review são obrigatórios)

### Anti-Patterns (EVITE)
- ❌ "God Agent" que faz tudo
- ❌ Agentes com múltiplos propósitos não relacionados
- ❌ Contexto excessivo entre agentes
- ❌ Pipeline paralela sem orquestração clara

## Output Esperado

Após a análise, você deve produzir:

1. **Arquivo de plano** em `.n8n_workflows/plans/[workflow-name]-plan.md`
2. **Lista de commands** que serão criados (próximo passo)
3. **Estrutura de nodes** do workflow n8n

## Checklist de Conclusão
- [ ] Workflow decomposto em agentes especializados
- [ ] Cada agente tem único propósito claro
- [ ] Pipeline sequencial definida
- [ ] Plano salvo em arquivo .md
- [ ] Estrutura de nodes mapeada
- [ ] Context flow documentado
