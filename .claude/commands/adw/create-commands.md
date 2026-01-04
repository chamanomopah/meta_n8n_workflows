---
description: Cria custom commands baseados no plano da pipeline seguindo padrão de qualidade SDLC
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, Glob, Grep
model: claude-sonnet-4-5-20250929
---

# Criar Custom Commands - Pipeline ADW

## Contexto
Você deve criar os custom commands especificados no arquivo de plano gerado pelo `/adw:plan-pipeline`.

**Arquivo de plano:** `$ARGUMENTS`
**Localização esperada:** `.n8n_workflows/plans/[workflow-name]-plan.md`

## Princípios de Qualidade (SDLC)

### Frontmatter YAML Obrigatório
Cada command DEVE ter:
```yaml
---
description: Breve descrição do que o command faz (aparece no /help)
argument-hint: [param1] [param2]  # Hint para auto-complete
allowed-tools: Bash, Read, Write, Edit  # Tools necessárias
---
```

### Estrutura de Commands
```markdown
# Nome do Command

## Contexto & Variáveis
[O que este command precisa saber]

## Tarefa Específica
[Passo a passo do que deve ser feito - UM propósito]

## Output Esperado
[O que este command deve produzir]
```

## Diretório de Trabalho

Cada workflow deve ser criado em:
```
C:\.n8n_workflows\projects\
  └── [#ordem]-[nome_do_workflow]\
      ├── README.md              (contexto do workflow)
      ├── workflow.json          (estrutura n8n - criado no passo 3)
      └── .claude\
          └── commands\
              ├── command-1.md   (agent 1)
              ├── command-2.md   (agent 2)
              └── command-n.md   (agent n)
```

## Sua Tarefa

### 1. Ler o Arquivo de Plano
```bash
Read `$ARGUMENTS`
```

Extraia:
- Lista de agentes/commands
- Purpose de cada agente
- Inputs/outputs esperados
- Ordem sequencial

### 2. Determinar Número do Workflow
Verifique workflows existentes em `C:\.n8n_workflows\projects\` para determinar o próximo número sequencial.

### 3. Criar Diretório do Projeto
```bash
mkdir "C:\.n8n_workflows\projects\#[numero]-[nome_do_workflow]"
mkdir "C:\.n8n_workflows\projects\#[numero]-[nome_do_workflow]\.claude\commands"
```

### 4. Criar README.md
Template:
```markdown
# [Nome do Workflow]

## Descrição
[Objetivo do workflow]

## Pipeline de Commands
1. `/adw:[command-1]` - [purpose]
2. `/adw:[command-2]` - [purpose]
[...]

## Estrutura de Nodes (n8n)
- Webhook (trigger)
- Set $arguments (se necessário)
- Execute Command → [command-1]
- Execute Command → [command-2]
[...]

## Contexto
[Informações relevantes para execução]

## Criado em
[Data]
```

### 5. Criar Cada Custom Command

Para cada agente do plano, crie um arquivo `.md` em `.claude/commands/`:

**Template de Command:**
```markdown
---
description: [Purpose em uma frase]
argument-hint: [params se necessário]
allowed-tools: [tools necessárias]
---

# [Nome do Command - Agente Especializado]

## Contexto
[O que este agente precisa saber antes de executar]

## Inputs
- [input 1]
- [input 2]

## Task (One Purpose)
[Passo a passo detalhado da ÚNICA tarefa que este agente executa]

**Foco**: [Qual etapa do SDLC: plan | build | test | review | document]

## Output
[O que este agente deve produzir]

## Validação
- [ ] Critério 1
- [ ] Critério 2
```

### 6. Regras de Qualidade por Etapa SDLC

#### Plan Commands
- **Purpose**: Analisar e especificar
- **Output**: Arquivo de specs/plano
- **Tools**: Read, Grep, Glob
- **Foco**: "O que estamos construindo?"

#### Build Commands
- **Purpose**: Criar e implementar
- **Output**: Arquivos/código criados
- **Tools**: Write, Edit, Bash
- **Foco**: "Fizemos acontecer?"

#### Test Commands
- **Purpose**: Validar e verificar
- **Output**: Relatório de testes
- **Tools**: Bash(test), Read
- **Foco**: "Funciona?"

#### Review Commands
- **Purpose**: Comparar com plano original
- **Output**: Relatório de review
- **Tools**: Read, Grep
- **Foco**: "É o que planejamos?"

#### Document Commands
- **Purpose**: Documentar uso e API
- **Output**: README/docs
- **Tools**: Write, Edit
- **Foco**: "Como funciona?"

## Padrão de Nomenclatura

### Commands
- **Nome**: `[action]-[resource].md`
- **Exemplos**:
  - `create-webhook-node.md`
  - `validate-workflow.md`
  - `generate-readme.md`

### Diretórios
- **Nome**: `#[numero]-[nome-claro]`
- **Exemplo**: `#001-slack-webhook-integration`

## Validação Final

Antes de finalizar, verifique:

- [ ] Todos os agents do plano foram criados
- [ ] Cada command tem frontmatter válido
- [ ] Cada command tem único propósito claro
- [ ] Diretório está em `C:\.n8n_workflows\projects\`
- [ ] README.md criado com contexto
- [ ] Namespacing correto (`adw:`)
- [ ] Commands seguem padrão SDLC

## Output Esperado

```
## Criados com Sucesso

### Projeto: #[numero]-[nome_do_workflow]
**Localização:** `C:\.n8n_workflows\projects\#[numero]-[nome_do_workflow]\`

### Commands Criados
1. `/adw:[command-1]` - [purpose]
2. `/adw:[command-2]` - [purpose]
[...]

### Estrutura
```
#.[numero]-[nome_do_workflow]\
├── README.md
├── workflow.json (A SER CRIADO no passo 3)
└── .claude\
    └── commands\
        ├── [command-1].md
        ├── [command-2].md
        └── [command-n].md
```

### Próximo Passo
Execute `/adw:create-workflow [plan-file]` para criar o workflow no n8n.
```

## Exemplo Prático

**Plano de Entrada:**
```markdown
## Pipeline Structure
### Agent 1: slack-webhook-planner
- Purpose: "Especificar nodes do webhook Slack"
- Output: "specs/slack-webhook.md"

### Agent 2: workflow-builder
- Purpose: "Criar workflow.json com estrutura base"
- Input: "specs/slack-webhook.md"
- Output: "workflow.json"
```

**Saída Gerada:**
```
C:\.n8n_workflows\projects\#001-slack-webhook\
├── README.md
└── .claude\commands\
    ├── plan-webhook.md      (Agent 1)
    └── build-workflow.md    (Agent 2)
```

## Anti-Patterns

❌ **NÃO FAZER:**
- Criar commands sem frontmatter
- Misturar múltiplos propósitos em um command
- Esquecer de criar README.md
- Usar nomes confusos ou genéricos
- Pular validação de estrutura

✅ **FAZER:**
- Seguir padrão SDLC
- Um purpose por command
- Documentar inputs/outputs
- Validar antes de finalizar
- Usar nomes descritivos
