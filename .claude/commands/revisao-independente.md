---
description: Revisão independente do diff atual pelo agente revisor (tarefas de risco alto)
---
Use o subagente `revisor` para revisar o diff atual da tarefa $ARGUMENTS.

Passe ao revisor apenas:
- o ID e a descrição da tarefa;
- a lista de arquivos alterados;
- os volumes e ADRs relevantes.

Não passe o raciocínio da implementação.

Depois, apresente os achados do revisor classificados por gravidade (crítico, alto, médio, baixo). Diga quais você corrigiu e quais exigem decisão do responsável. Não descarte achados sem justificar.
