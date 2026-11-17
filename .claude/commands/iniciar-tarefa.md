---
description: Lê uma tarefa do backlog e produz o plano obrigatório antes de codificar
argument-hint: <ID da tarefa, ex. R1-07>
---
Tarefa: $ARGUMENTS

1. Confirme a branch atual (`git branch --show-current`). Se for `main`, pare e avise.
2. Localize a tarefa em `docs/12_ROADMAP_RELEASES_E_BACKLOG.md` e os requisitos que ela cobre em `docs/02_REQUISITOS.md`. Leia só os volumes e ADRs citados e o código relacionado.
3. Verifique se a tarefa anterior foi aceita e se esta pertence à release em andamento. Se não, pare e avise.
4. Apresente o plano conforme `docs/13_GUIA_DE_EXECUCAO.md` §5.1:
   - ID e requisitos cobertos
   - objetivo e contexto
   - arquivos e módulos afetados
   - impacto em API, banco, telas, permissões, dados, memória e tempo de resposta
   - riscos e plano de reversão
   - passos pequenos de implementação
   - testes por camada (Volume 09 §2)
   - critérios de aceite verificáveis
   - para telas: a tela correspondente no modelo aprovado do Claude Design (Volume 07 §17.1); se ela exigir padrão novo, peça aprovação antes de codificar
5. Liste os itens que exigem aprovação (Guia §4.2). Se houver algum, **aguarde a aprovação** antes de alterar qualquer arquivo.
6. Termine com perguntas objetivas sobre o que estiver ambíguo, com opções.
