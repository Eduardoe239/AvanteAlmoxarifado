---
description: Autorrevisão em duas etapas sobre o diff atual
---
Revise o diff atual (`git diff` e `git diff --staged`) conforme `docs/13_GUIA_DE_EXECUCAO.md` §5.3.

**Etapa 1 — funcional e técnica**
- O requisito da tarefa foi atendido por completo?
- Rode as verificações pertinentes (`make check` ou as ferramentas de cada parte) e mostre a saída resumida real.
- Os testes falhariam se o código estivesse errado? Aponte testes fracos.
- Contratos de API, QR e dispositivos continuam compatíveis?
- Percorra o checklist de `docs/09_QUALIDADE_E_TESTES.md` §8 item por item.

**Etapa 2 — revisão de quem desconfia**
Procure ativamente:
- falhas de lógica e condições de corrida;
- autorização horizontal e vertical;
- saldo alterado fora do ledger;
- casos extremos (vazio, máximo, unicode, fuso, fração, repetição, rede caindo);
- acessibilidade;
- N+1, índice ausente, payload grande e consumo de memória acima do orçamento;
- segredos ou dados pessoais;
- acoplamento e complexidade desnecessários;
- documentação desatualizada.

Corrija o que encontrar, repita a Etapa 1 e relate o que foi achado e corrigido. Se a tarefa for de risco alto, recomende `/revisao-independente`.
