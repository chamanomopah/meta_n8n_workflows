---
description: Validar correções aplicadas e testar workflow modificado
argument-hint: <workflow_id>
allowed-tools: Bash, Read, Write, Edit, mcp__n8n-mcp__n8n_validate_workflow, mcp__n8n-mcp__n8n_get_workflow, mcp__n8n-mcp__n8n_test_workflow
---

# Validate Fix - Agente Especialista em Validação

## Contexto
Este agente especialista é responsável por validar que as correções aplicadas pelo Agent 2 funcionam corretamente. Ele deve testar a estrutura do workflow, validar configurações e opcionalmente executar um teste real se o workflow tiver triggers apropriados.

## Inputs
- **$ARGUMENTS**:
  - `workflow_id`: ID do workflow n8n modificado que deve ser validado

## Task (One Purpose - SDLC TEST)

Você deve executar as seguintes etapas sequencialmente:

### 1. Parse Arguments
Extrair `workflow_id` de `$ARGUMENTS`:
- Único argumento = ID do workflow a validar

### 2. Obter Workflow Atual
Usar `n8n_get_workflow` para recuperar estado atual:
- Modo: `structure` (nodes + connections)
- Verificar que workflow existe
- Extrair lista de nodes e configurações

### 3. Validar Estrutura do Workflow
Usar `n8n_validate_workflow` para validação completa:

```python
mcp__n8n-mcp__n8n_validate_workflow(
  id=workflow_id,
  options={
    "validateNodes": True,
    "validateConnections": True,
    "validateExpressions": True,
    "profile": "runtime"
  }
)
```

**Verificar:**
- [ ] Nodes válidos (sem erros de configuração)
- [ ] Conexões corretas (todos os inputs conectados)
- [ ] Expressões sintaticamente corretas
- [ ] Sem warnings críticos

### 4. Análise Comparativa
Comparar com estado original (se disponível):

#### Ler Arquivo de Implementação
Tentar ler `specs/[problem-name]-implementation.md`:
- Extrair operações aplicadas
- Verificar que mudanças planejadas foram aplicadas
- Validar que nodes mencionados existem

#### Verificar Mudanças Específicas
Para cada operação do relatório:
- **updateNode**: Verificar que parâmetros foram alterados
- **addConnection**: Verificar que conexão existe
- **updateSettings**: Verificar que settings foram atualizados

### 5. Teste de Execução (Opcional)
Se o workflow tiver trigger apropriado (webhook/form/chat):

#### Detectar Tipo de Trigger
Usar `n8n_get_workflow` mode=`structure`:
- Procurar node do tipo `n8n-nodes-base.webhook`
- Procurar node do tipo `n8n-nodes-base.form`
- Procurar node do tipo `n8n-nodes-base.chatTrigger`

#### Executar Teste Se Possível
```python
# Para webhook trigger
mcp__n8n-mcp__n8n_test_workflow(
  workflowId=workflow_id,
  triggerType="webhook",
  httpMethod="POST",
  data={
    "test": "validation"
  },
  waitForResponse=True
)
```

**Se teste executar:**
- Verificar que completa sem erros
- Capturar output de cada node
- Validar que nodes críticos executaram

**Se teste falhar:**
- Capturar erro completo
- Identificar node que falhou
- Determinar se é problema de teste ou da correção

**Se não houver trigger testável:**
- Validar estrutura apenas
- Marcar como "validation_only"

### 6. Gerar Relatório Final
Criar arquivo `specs/[problem-name]-validation.md` com:

#### Frontmatter
```yaml
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
validation_date: "2025-01-05"
status: "passed" | "failed" | "partial"
validation_type: "full" | "structure_only"
---
```

#### Seções do Documento

**1. Resumo da Validação**
- Status final (passed/failed/partial)
- Tipo de validação executada
- Workflow ID validado

**2. Validação de Estrutura**
- Status: ✓ Passed / ✗ Failed
- Nodes válidos: [N] de [total]
- Conexões válidas: [N] de [total]
- Expressões válidas: [N] de [total]
- Erros encontrados: [lista ou "none"]

**3. Verificação de Mudanças**
Para cada operação do plano original:
- [✓] updateNode: Webhook timeout alterado para 120000
- [✓] updateSettings: executionTimeout alterado para 180000
- [✓] addConnection: Node A → Node B criada

**4. Teste de Execução** (se aplicável)
- Status: ✓ Passed / ✗ Failed / ⊘ Skipped
- Trigger type: [webhook|form|chat|none]
- Execution time: [X]s
- Nodes executados: [N] de [total]
- Erros: [none ou lista]

**5. Diagnóstico Final**
- Workflow está funcional: Sim/Não
- Correções aplicadas com sucesso: Sim/Não
- Problema original resolvido: Sim/Não/Parcial

**6. Recomendações**
- Próximos passos
- Sugestões de rollback se falhou
- Melhorias adicionais sugeridas

### 7. Output Final
Imprimir no stdout:

**Caso Passed:**
```
✓ Validation passed
File: specs/[problem-name]-validation.md
Workflow: [workflow_id]
Status: All corrections working correctly
Test: [passed|structure_only]
```

**Caso Failed:**
```
✗ Validation failed
File: specs/[problem-name]-validation.md
Workflow: [workflow_id]
Status: [error description]
Rollback: Consider using n8n_workflow_versions to rollback
```

**Caso Partial:**
```
⚠ Validation partial
File: specs/[problem-name]-validation.md
Workflow: [workflow_id]
Status: [what passed, what failed]
Review: Manual inspection required
```

**Foco SDLC**: TEST - "As correções funcionam como esperado?"

## Output

### Arquivo Criado
- **Caminho**: `specs/[problem-name]-validation.md`
- **Conteúdo**: Relatório completo de validação

### Stdout
- Status final (passed/failed/partial)
- Caminho do relatório de validação
- Workflow ID validado
- Resumo do que foi testado
- Recomendações se falhou

## Validação

- [ ] Argumento (workflow_id) parseado corretamente
- [ ] Workflow recuperado com sucesso
- [ ] Validação de estrutura executada
- [ ] Mudanças específicas verificadas
- [ ] Teste de execução executado se trigger disponível
- [ ] Relatório de validação criado
- [ ] Frontmatter com status correto
- [ ] Stdout com resumo claro
- [ ] Recomendações apropriadas para status

## Exemplo de Uso

**Input:**
```
$ARGUMENTS = "BVEJpyeRuGrNnruQ"
```

**Output (Passed):**
```
✓ Validation passed
File: specs/webhook-timeout-validation.md
Workflow: BVEJpyeRuGrNnruQ
Status: All corrections working correctly
Test: passed (execution time: 2.3s, 5/5 nodes)
```

**Arquivo Gerado:** `specs/webhook-timeout-validation.md`
```markdown
---
workflow_id: "BVEJpyeRuGrNnruQ"
problem_name: "webhook-timeout"
status: "passed"
validation_type: "full"
---

## Resumo da Validação
Workflow validado com sucesso. Todas as correções aplicadas estão funcionando corretamente.

## Validação de Estrutura
- Status: ✓ Passed
- Nodes válidos: 5 de 5
- Conexões válidas: 4 de 4
- Expressões válidas: 2 de 2

## Teste de Execução
- Status: ✓ Passed
- Trigger type: webhook
- Execution time: 2.3s
- Nodes executados: 5 de 5

## Diagnóstico Final
- Workflow está funcional: Sim
- Correções aplicadas com sucesso: Sim
- Problema original resolvido: Sim

## Recomendações
✓ Workflow pronto para produção
✓ Monitorar próximas 10 execuções
```

**Output (Failed):**
```
✗ Validation failed
File: specs/webhook-timeout-validation.md
Workflow: BVEJpyeRuGrNnruQ
Status: Expression error in node 'Process Data'
Rollback: Use n8n_workflow_versions mode=rollback versionId=42
```

## Notas Importantes

1. **Validação Estrutural vs. Funcional**: Sempre validar estrutura, mas teste funcional depende de trigger disponível
2. **Rollback**: Se validação falhar, considerar usar `n8n_workflow_versions` para rollback
3. **Warnings**: Warnings não críticos devem ser reportados mas não causam falha
4. **Logs**: Manter logs detalhados de todas as validações para auditoria
