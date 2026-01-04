A tua experiência está bem alinhada com os “pontos de dor” reais de rodar CLIs interativas dentro do **Execute Command** do n8n (principalmente no Windows). A diferença é que, nas docs oficiais do n8n, a história “correta” não é “habilitar via `N8N_ALLOW_EXECUTE_COMMAND`”, e sim entender 2 mecanismos distintos:

1) **O node Execute Command existe, mas vem BLOQUEADO por padrão via lista de nós** (a partir do n8n 2.0)  
2) **Ele executa no shell padrão e no runtime onde o n8n está rodando (host vs container vs worker)**

Abaixo vai uma documentação “de verdade” (mais técnica, com boas práticas e decisões), usando tua base e o que está nas docs oficiais do n8n.

## esse documento é complemento ao: cc_cli_in_n8n.md

---

# Documento único: Boas práticas para rodar Claude Code CLI via Execute Command no n8n (local/self-hosted)

## 1) [n8n Execute Command](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/): o que ele realmente faz e onde roda

O **Execute Command** “roda comandos shell na máquina host que roda o n8n”, usando **o shell padrão do sistema** (ex.: `cmd` no Windows, `zsh` no macOS). Se você roda n8n via **Docker**, o comando roda **dentro do container do n8n**, não no host. Em **queue mode**, em produção, o comando roda no **worker** que pegou o job (manual execution roda no main, a menos que você faça offload). [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)

### Implicações práticas (as que pegam na vida real)
- **Seu “ambiente” é o do processo do n8n**: PATH, permissões, usuário, diretório, variáveis.
- **Em Docker**, “instalar claude no host” não adianta: o binário precisa existir no container (ou você chama um serviço externo).
- **Em queue mode**, se você tem múltiplos workers, cada worker precisa ter o Claude CLI disponível e acesso ao workspace/código.

---

## 2) Por que o Execute Command “roda mas não roda” no n8n 2.0+ (o motivo oficial)

O Execute Command é considerado de **alto risco** e por isso fica **desabilitado por padrão** a partir do n8n 2.0. O mecanismo oficial é via `NODES_EXCLUDE` (lista de nós bloqueados). [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)  

A docs de nodes mostra explicitamente que o default do `NODES_EXCLUDE` inclui:
- `n8n-nodes-base.executeCommand`
- `n8n-nodes-base.localFileTrigger`  
[Source](https://docs.n8n.io/hosting/configuration/environment-variables/nodes/)

E a docs de “blocking nodes” explica como liberar:
- Para habilitar todos os nós bloqueados por default: `NODES_EXCLUDE: "[]"`  
[Source](https://docs.n8n.io/hosting/securing/blocking-nodes/)

### Recomendação técnica (melhor prática)
Em vez de “habilitar geral”, prefira **higienizar o mínimo necessário**:
- Se o objetivo é habilitar só Execute Command, você remove ele do exclude (na prática, o n8n trabalha com “exclude list”; então ou você seta `[]` e compensa com controles operacionais, ou você mantém o resto bloqueado conforme seu risco).

> Observação: tua anotação de `N8N_ALLOW_EXECUTE_COMMAND=true` pode ter sido válida numa versão/guia antigo ou em algum wrapper, mas o caminho documentado hoje é **`NODES_EXCLUDE`** (e é exatamente por isso que muita gente “se perde” — houve mudança comportamental importante no 2.0).

---

## 3) Onde “morre” a automação: stdin/TTY e CLIs semi-interativas (teu caso do Claude)

### Sintoma clássico
- Execução fica “infinita” ou parece travada.
- O CLI espera input (stdin aberto) ou tenta comportamento de TTY.

### Tua solução (fechar stdin) é padrão-ouro
No Windows, redirecionar `< NUL` funciona como “EOF imediato”. Isso evita o CLI ficar aguardando input. É um padrão clássico de automação de CLI em ambientes sem TTY.

**Equivalentes:**
- Windows: `< NUL`
- Linux/macOS: `< /dev/null`

**Boa prática adicional:** sempre capture stderr para depuração:
- `2>&1`

---

## 4) [Execute Command common issues](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/common-issues/): erros que vão aparecer quando você escalar

### 4.1 “command not found”
Se o shell não acha o comando:
- Pode ser PATH (usuário do processo do n8n não tem o mesmo PATH do seu terminal)
- Pode ser Docker (binário não existe no container)

A docs recomenda checar:
- typos
- PATH do usuário do n8n
- se está no container (e até executar dentro do container pra validar)  
[Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/common-issues/)

**Melhor prática:** use caminho absoluto do executável (`C:\...\claude.exe` ou equivalente) quando possível.

### 4.2 “stdout maxBuffer length exceeded”
Se o comando devolve output grande demais, o node pode falhar. A recomendação é **reduzir output**, usar flags de filtro/limite, ou pipeline para “cortar”. [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/common-issues/)

**Aplicação direta ao Claude:**
- Prefira `--output-format json` (quando você vai parsear) e mantenha prompts/retornos controlados.
- Não deixe o Claude “printar” dumps enormes; peça “resumo + diff” ou “apenas patch”.

---

## 5) Segurança e isolamento (o ponto que quase ninguém documenta direito)

O Execute Command “abre a máquina” para execução arbitrária. Por isso o n8n recomenda bloquear nós perigosos quando usuários não são plenamente confiáveis. [Source](https://docs.n8n.io/hosting/securing/blocking-nodes/)

### Controles recomendados (camadas)
1) **Isolamento por ambiente**
   - Se possível, rode n8n + Claude em VM/contêiner dedicado só para automações.
2) **Princípio do menor privilégio (filesystem)**
   - Crie um “workspace” (ex.: `C:\n8n-workspaces\projA`) e não rode em `C:\Users\...` se você quer operar mais “server-like”.
3) **Restrição de acesso a arquivos pelo próprio n8n**
   - `N8N_RESTRICT_FILE_ACCESS_TO` permite limitar acesso a diretórios específicos (lista separada por `;`). [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)
   - `N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES=true` (default) bloqueia acesso à pasta `.n8n` e configs. [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)
4) **Controle de exposição de segredos**
   - `N8N_BLOCK_ENV_ACCESS_IN_NODE` pode bloquear acesso a env vars via expressões/Code Node. [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)
5) **Claude “danger mode”**
   - `--dangerously-skip-permissions` é funcional para automação, mas ele remove uma barreira de segurança do Claude. Use junto com isolamento de máquina/pasta e preferencialmente com repositórios “descartáveis” (clone temp) quando a automação for agressiva.

---

## 6) Escalando “várias instâncias do Claude” no n8n: concorrência de verdade

Aqui tem 2 níveis: concorrência do n8n e concorrência do Claude.

### 6.1 Concorrência do n8n (regular mode)
Por padrão, em regular mode, n8n não limita concorrência de execuções em produção; você pode habilitar limite com `N8N_CONCURRENCY_PRODUCTION_LIMIT`. [Source](https://docs.n8n.io/hosting/scaling/concurrency-control/)  
Essa variável também aparece na lista de env vars de execução. [Source](https://docs.n8n.io/hosting/configuration/environment-variables/executions/)

**Importante:** isso vale para execuções “production” (webhook/trigger), não necessariamente para manual/subworkflow etc. [Source](https://docs.n8n.io/hosting/scaling/concurrency-control/)

### 6.2 Escala correta (queue mode)
Se você realmente quer “rodar várias instâncias” com estabilidade, **queue mode** é a arquitetura recomendada:
- `EXECUTIONS_MODE=queue`
- Redis como broker
- workers executando jobs  
[Source](https://docs.n8n.io/hosting/scaling/queue-mode/)

E você controla paralelismo por worker com `n8n worker --concurrency=<n>`. [Source](https://docs.n8n.io/hosting/scaling/queue-mode/)

**Ponto crítico do Execute Command em queue mode:** o comando vai rodar **no worker** que processar. [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)

Então, “boas práticas” para múltiplas instâncias do Claude:
- Garantir que **Claude CLI + config + credenciais** existam em **todos os workers**
- Garantir que **workspace** exista e esteja acessível (volume compartilhado, ou clone por execução)

---

## 7) Padrão de comando recomendado (Windows) — robusto para produção

### 7.1 Template (com logs e sem travar stdin)
```bat
cd /d "C:\workspaces\adw_in_n8n" ^
 && "C:\caminho\para\claude.exe" -p "SEU PROMPT" --dangerously-skip-permissions --output-format json < NUL 2>&1
```

**Por quê:**
- `cd /d` garante troca de drive + pasta
- caminho absoluto do `claude.exe` evita “command not found”
- `--output-format json` ajuda parsing (e torna output mais previsível)
- `< NUL` evita hang
- `2>&1` ajuda a não perder erro

### 7.2 Padrão para “Plan → Build → Test” com artefatos previsíveis
- Sempre produzir arquivos com nomes determinísticos (`specs.md`, `patch.diff`, `report.json`)
- Evitar que o Claude “escolha nomes”
- Sempre pedir “saída curta no stdout” e “artefato no disco”

Isso reduz risco de estourar buffer e facilita observabilidade.

---

## 8) Docker: como não cair na armadilha do “no host funciona”

O Execute Command em Docker roda **no container**, então:
- Claude CLI precisa estar instalado no container, ou você constrói imagem customizada (o n8n mostra exemplo de custom image até para instalar `curl`). [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)

**Boa prática:** em vez de instalar “coisas” no container do n8n, muitas equipes preferem:
- Manter n8n “limpo”
- Chamar um “runner service” externo (HTTP) que executa Claude num ambiente controlado

Mas se você quer tudo local, imagem customizada é o caminho “oficial-style”.

---

## 9) Checklist técnico (refinado) para Claude CLI + Execute Command

### Configuração n8n (self-hosted)
- Execute Command habilitado via `NODES_EXCLUDE: "[]"` (ou ajuste equivalente) [Source](https://docs.n8n.io/hosting/securing/blocking-nodes/)  
- Entender onde roda: host vs docker vs worker [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
- Se for escalar: considerar queue mode [Source](https://docs.n8n.io/hosting/scaling/queue-mode/)

### Confiabilidade do comando
- Usar `-p`/modo não-interativo
- Fechar stdin (`< NUL` / `< /dev/null`)
- Capturar stderr (`2>&1`)
- Controlar tamanho de output (evitar maxBuffer) [Source](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/common-issues/)

### Segurança
- Restringir acesso a arquivos (`N8N_RESTRICT_FILE_ACCESS_TO`) [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)
- Não expor `.n8n` (default já bloqueia) [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)
- Considerar bloquear acesso a env vars em expressões (dependendo do seu modelo de ameaça) [Source](https://docs.n8n.io/hosting/configuration/environment-variables/security/)

---

## Fontes oficiais (navegação rápida)
- [Execute Command](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)  
- [Execute Command – Common issues](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/common-issues/)  
- [Nodes env vars (NODES_EXCLUDE)](https://docs.n8n.io/hosting/configuration/environment-variables/nodes/)  
- [Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/)  
- [Executions env vars (EXECUTIONS_MODE, timeouts, etc.)](https://docs.n8n.io/hosting/configuration/environment-variables/executions/)  
- [Queue mode](https://docs.n8n.io/hosting/scaling/queue-mode/)  
- [Concurrency control](https://docs.n8n.io/hosting/scaling/concurrency-control/)  
- [Security env vars (restrict file/env access)](https://docs.n8n.io/hosting/configuration/environment-variables/security/)

---

## Próximo passo (pra eu fechar 100% no teu cenário)
Você quer essa “documentação completa em 1 arquivo” focada em qual setup principal?

1) Windows rodando n8n via `n8n start` (sem Docker)  
2) Windows + Docker (WSL2/Hyper-V)  
3) Linux server + Docker + queue mode + workers  

E: quando você diz “rodar várias instâncias de Claude Code”, você quer **paralelizar dentro do mesmo workflow** (ex.: split em itens) ou quer **várias execuções simultâneas de workflows** (multi-tenant / webhooks concorrentes)?