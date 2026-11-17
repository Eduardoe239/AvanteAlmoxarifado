---
description: Gera o relatório de entrega com resultados reais
---
Gere o relatório de entrega da tarefa atual exatamente no formato de `docs/13_GUIA_DE_EXECUCAO.md` §5.4.

Regras:
- Use apenas comandos realmente executados nesta sessão e as saídas reais, com contagens exatas. O que não foi executado vai em "Testes não executados e motivo".
- Em "Impacto em memória e tempo de resposta", informe o valor medido ou escreva "não medido".
- Em "Como o responsável verifica", dê passos curtos para testar em aparelho real.
- Status:
  - PASS só com todos os critérios atendidos e evidenciados;
  - HOLD quando falta algo, dizendo o que desbloqueia;
  - FAIL quando algo falhou.
- Termine sugerindo a mensagem de commit (Conventional Commits em português, com o ID). Não faça commit nem push sem autorização.
