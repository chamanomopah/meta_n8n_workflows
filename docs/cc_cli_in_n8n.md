

# Guia Completo: n8n + Claude Code CLI

## Análise da Jornada e Lições Aprendidas

---

## 1. Conceitos Fundamentais

### O que é Claude Code CLI?

O **Claude Code** é uma ferramenta de linha de comando que permite interagir com o Claude de forma programática para tarefas de desenvolvimento, como análise de código, criação de arquivos e edição de codebases. (sempre usar o caminho a ser usado )

### Modos de Operação

| Modo | Comando | Uso |
|------|---------|-----|
| **Interativo (REPL)** | `claude` | Terminal manual, conversação |
| **Print Mode** | `claude -p "query"` | Executa e sai, ideal para automação |
| **Continue** | `claude -c` | Continua última conversa |
| **Resume** | `claude -r "id"` | Retoma sessão específica |

### Por que integrar com n8n?

O n8n permite orquestrar múltiplas chamadas ao Claude Code em **workflows sequenciais**, criando pipelines de automação como:
- **Plan → Build → Test**
- **Análise → Geração de Specs → Implementação**
- **Code Review → Correção → Deploy**

---

## 2. Testes que Falharam e Por Quê

### ❌ Falha 1: `stdout` Vazio com `exitCode: 0`

**Comando testado:**
```bash
cd /d C:\Users\Lofrey\Downloads\Projetos\adw_in_n8n && claude --print "Diga apenas: OK"
```

**Resultado:**
```json
{"exitCode": 0, "stderr": "", "stdout": ""}
```

**Por que falhou:**
- O n8n 2.0+ **desabilita o Execute Command por padrão** por segurança
- O node executava mas estava bloqueado silenciosamente

**Solução:**
```bash
set N8N_ALLOW_EXECUTE_COMMAND=true
n8n start
```

---

### ❌ Falha 2: Comando Rodando Infinitamente

**Comando testado:**
```bash
cd /d C:\Users\Lofrey\Downloads\Projetos\adw_in_n8n && claude -p "Diga OK" --dangerously-skip-permissions
```

**Resultado:** Workflow travava indefinidamente.

**Por que falhou:**
- O Claude CLI aguardava **input do stdin**
- Em modo não-interativo via n8n, o stdin não era fechado automaticamente
- O CLI ficava bloqueado esperando entrada que nunca chegava

**Solução - Fechar stdin explicitamente:**
```bash
claude -p "query" --dangerously-skip-permissions < NUL
```

| Método | Sintaxe Windows | Explicação |
|--------|-----------------|------------|
| **Redirecionar NUL** | `< NUL` | Fecha stdin imediatamente |
| **Pipe vazio** | `echo. \|` | Envia input vazio e fecha |

---

### ❌ Falha 3: Flag `--print` vs `-p`

**Observação:** Ambas funcionam, mas `-p` é a forma abreviada documentada oficialmente e mais confiável para automação.

---

## 3. Configuração que Funciona

### Pré-requisitos

```bash
# 1. Variáveis de ambiente (CMD Windows)
set N8N_ALLOW_EXECUTE_COMMAND=true
set NODES_EXCLUDE=""

# 2. (Opcional) Webhook URL para acesso externo
set WEBHOOK_URL=https://seu-ngrok-url.ngrok-free.dev

# 3. Iniciar n8n
n8n start
```

### Padrão de Comando Funcional

```bash
cd /d [DIRETÓRIO] && claude -p "[PROMPT]" --dangerously-skip-permissions < NUL
```

| Elemento | Obrigatório | Propósito |
|----------|-------------|-----------|
| `cd /d [DIR]` | ✅ | Define diretório de trabalho |
| `claude -p` | ✅ | Modo print (não-interativo) |
| `--dangerously-skip-permissions` | ✅ | Pula prompts de confirmação |
| `< NUL` | ✅ | Fecha stdin (evita travamento) |
| `2>&1` | Opcional | Captura stderr no stdout |

---

## 4. Flags Importantes para Automação

| Flag | Uso | Exemplo |
|------|-----|---------|
| `-p "query"` | Executa e sai | `claude -p "liste arquivos"` |
| `--dangerously-skip-permissions` | Pula confirmações | Essencial para n8n |
| `--output-format json` | Retorna JSON estruturado | Melhor para parsing |
| `--output-format text` | Retorna texto puro | Padrão |
| `--max-turns 3` | Limita iterações do agente | Evita loops longos |
| `--model sonnet` | Define modelo | `sonnet` ou `opus` |
| `--verbose` | Log detalhado | Debug |

---

## 5. POC Realizado com Sucesso

### Objetivo
Criar workflow que:
1. **Analisa** código com bugs
2. **Gera** arquivo de especificações
3. **Implementa** correções automaticamente

### Arquivo de Teste (`calculator.js`)

```javascript
// calculator.js - arquivo com bugs intencionais
function soma(a, b) {
    return a - b; // BUG: deveria ser a + b
}

function multiplica(a, b) {
    return a / b; // BUG: deveria ser a * b
}

function divide(a, b) {
    return a * b; // BUG: deveria ser a / b
}

module.exports = { soma, multiplica, divide };
```

### Workflow Final

```
[Manual Trigger] → [Plan] → [Build]
```

**Node Plan:**
```bash
cd /d C:\Users\Lofrey\Downloads\Projetos\adw_in_n8n && claude -p "Analise o arquivo calculator.js, identifique todos os bugs nas funções matemáticas e crie um arquivo specs.md com o plano detalhado de correção" --dangerously-skip-permissions < NUL
```

**Node Build:**
```bash
cd /d C:\Users\Lofrey\Downloads\Projetos\adw_in_n8n && claude -p "Leia o arquivo specs.md e implemente todas as correções necessárias no arquivo calculator.js" --dangerously-skip-permissions < NUL
```

### Resultado

| Node | Output |
|------|--------|
| **Plan** | Criou `specs.md` com 3 bugs identificados e plano de correção |
| **Build** | Corrigiu `calculator.js` + adicionou validação de divisão por zero |

---

## 6. Workflow JSON Completo (Copiar e Importar)

```json
{
  "nodes": [
    {
      "parameters": {},
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [0, 0],
      "name": "Trigger"
    },
    {
      "parameters": {
        "command": "cd /d C:\\Users\\Lofrey\\Downloads\\Projetos\\adw_in_n8n && claude -p \"Analise calculator.js, identifique os bugs e crie specs.md com o plano de correção\" --dangerously-skip-permissions < NUL"
      },
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [220, 0],
      "name": "Plan"
    },
    {
      "parameters": {
        "command": "cd /d C:\\Users\\Lofrey\\Downloads\\Projetos\\adw_in_n8n && claude -p \"Leia specs.md e corrija os bugs em calculator.js\" --dangerously-skip-permissions < NUL"
      },
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [440, 0],
      "name": "Build"
    }
  ],
  "connections": {
    "Trigger": {"main": [[{"node": "Plan", "type": "main", "index": 0}]]},
    "Plan": {"main": [[{"node": "Build", "type": "main", "index": 0}]]}
  }
}
```

---

## 7. Alternativa Avançada: n8n-MCP Server

Para workflows mais complexos, considere usar o **n8n-MCP Server** que permite ao Claude criar workflows diretamente via API:

```bash
claude mcp add n8n-mcp \
  -e N8N_API_URL=http://localhost:5678 \
  -e N8N_API_KEY=sua-api-key \
  -- npx n8n-mcp
```

**Vantagens do MCP:**
- Claude pode **criar, editar e validar** workflows automaticamente
- Acesso à documentação dos nodes
- Troubleshooting automático de erros

---

## 8. Checklist para Novos Workflows


### Estrutura do Comando

- [ ] Usar `-p` para modo print
- [ ] Incluir `--dangerously-skip-permissions`
- [ ] Adicionar `< NUL` no final
- [ ] Usar `cd /d` para Windows

### Debugging

- [ ] Adicionar `2>&1` para capturar erros
- [ ] Usar `--verbose` para logs detalhados
- [ ] Verificar `stderr` no output do node
- [ ] Testar comando no terminal antes do n8n

---

## 9. O que Funciona vs O que Não Funciona

| ✅ Funciona | ❌ Não Funciona |
|-------------|-----------------|
| `claude -p "query" < NUL` | `claude --print "query"` (sem fechar stdin) |
| `--dangerously-skip-permissions` | Modo interativo no n8n |
| Comandos com diretório explícito | Paths relativos sem `cd` |
| `--output-format json` para parsing | Prompts muito longos sem quebra |
| Workflows sequenciais simples | Múltiplos comandos paralelos no mesmo diretório |

--