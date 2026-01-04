crie um primeiro template do adw no n8n que possue uma estrutura simples: 
adw_template_v1.json (que utiliza claude code cli pra executar custom commands)

quero 3 commandos pra automatizar a criação de adw no n8n 

1. pra planejar a pineline de commands e quantos ncessarios e cria um arquivo com plan com a pineline de slash commands, , a pineline precisa seguir uma estrutura de nodes onde sempre vai ser com base no adw_template_v*.json (ex: se tiver no workflow a estrutura de 1 node de webhook, 2 ou 1 set node (depende se o workflow precisar de $arguments) e a quantidade de execute commands )
2. cria os commands com base no plan. cada novo workflow precisa ser criado na pasta C:\.n8n_workflows\projects\[#numero daordemdoworkflow]-[nome_do_workflow]\ dentro com readme.md (contexto do workflow) e workflow.json  
3. cria o workflow no n8n com base na estrtura do template adw_template_v1.json e cria um novo workflow usando n8n-mcp tools e criar um novo


adendo: cada custom command vai servir pra 1 claude code agent então a quantidade de agentes depende da quantidade de custom commands

