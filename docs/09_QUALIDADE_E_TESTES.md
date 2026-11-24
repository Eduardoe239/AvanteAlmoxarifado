# Volume 09 — Qualidade e Testes

**Produto:** Avante Almoxarifado · **Versão:** 3.1.0 · **Data:** 24/11/2026 · **Status:** Aprovado em 24/11/2026
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** comprova os RNF do Volume 02; define a Definição de Pronto usada pelo Volume 12 e pelo Guia de Execução (Volume 13).

---

## 1. Princípios

1. **Teste junto com o comportamento:** nenhuma funcionalidade é entregue sem os testes que a comprovam, na mesma mudança.
2. **Banco real:** testes de integração rodam em PostgreSQL da mesma versão de produção, com o schema criado **só pelas migrations**.
3. **Nada mascarado:** sem `|| true`, sem `continue-on-error`, sem teste pulado sem tarefa aberta e prazo; um teste instável é corrigido ou removido com registro, nunca ignorado.
4. **Evidência, não declaração:** cada critério de release tem evidência anexada (relatório de CI, captura, planilha de medição, gravação). Resultado não medido é "não verificado", nunca "aprovado".
5. **Testar no hardware de verdade:** metas de desempenho valem no **Perfil Mínimo** (Volume 04) e são medidas no notebook real da Avante, não só na máquina do desenvolvedor.
6. **Desenvolvedor único, revisão obrigatória:** como não há segundo programador, toda mudança passa pela autorrevisão com checklist (§8) e pelo CI; mudanças de risco alto (dinheiro, saldo, segurança, migração) recebem uma segunda leitura no dia seguinte antes do merge.

## 2. Camadas de teste

| Camada | Ferramenta | O que garante | Onde roda |
|---|---|---|---|
| Unitário (backend) | pytest | Regras de domínio, políticas, validações | CI, a cada push |
| Propriedade | Hypothesis | Invariantes: saldo = Σ movimentações; transições de estado válidas; QR com dígito verificador | CI |
| Integração | pytest + PostgreSQL real | Toda rota; constraints; transações; autorização | CI (Linux; Windows a partir da R0 para a camada de plataforma, completo na R4) |
| Concorrência | Processos paralelos contra PostgreSQL | Última unidade disputada; transferências simultâneas; QR repetido; idempotência | CI |
| Migrations | Alembic | Vazio → atual; N-1 com dados → N; `alembic check` sem divergência | CI |
| Contrato | OpenAPI + cliente TypeScript gerado | Mudança incompatível quebra o CI | CI |
| Tempo real | Integração de SSE e Web Push | Entrega, reconexão, filtragem por permissão | CI |
| Plataforma | Testes da camada `backend/src/avante/platform/` | Serviços, caminhos, permissões, backup e restauração | CI (Linux e Windows) |
| Frontend | Vitest + Testing Library | Componentes, hooks, formatação de datas | CI |
| E2E | Playwright (Chromium, WebKit, Firefox, perfis móveis) | Fluxos críticos de cada papel, inclusive dois usuários interagindo | CI (fluxos críticos a cada PR; suíte completa por noite) |
| Acessibilidade | axe-core + revisão manual com TalkBack, VoiceOver e NVDA | RNF-04 | CI + manual por release |
| Visual | Capturas do Playwright por tema e ponto de quebra; Storybook | Sem regressão visual não aprovada | CI |
| Desempenho percebido | Lighthouse CI + medição em aparelho real | RNF-18 | CI + manual por release |
| Usabilidade | Testes moderados com tarefas reais e SUS | RNF-19 | Por release (Volume 07 §17) |
| Segurança | Bandit/Semgrep, pip-audit, OSV-Scanner, gitleaks, ZAP baseline, verificação de licenças | RNF-08, RNF-17 | CI + ZAP por release |
| Carga | k6 | RNF-05 | Notebook real, por release |
| Recursos | Medição de RAM, CPU e I/O dos serviços | RNF-20, RNF-22 | Notebook real, por release |
| Recuperação | Roteiros automatizados | RNF-06, RNF-07, RNF-14 | Homologação, por release |
| Visão computacional | Protocolo do Volume 05 §5 | RNF-23 | CI (subconjunto) + avaliação completa por versão de modelo |
| Firmware | Unity no host; análise estática; bancada (Volume 05 §7) | RNF-24 | CI + bancada por versão |
| Aparelhos reais | Matriz do §4 | Câmera, instalação, push, layout | Por release |

## 3. Testes no Perfil Mínimo (notebook real)

O notebook da Avante é o **ambiente de homologação** da R0 até a entrada em produção, na R1. A partir daí, a homologação passa para uma **VM limitada a 2 vCPU e 4 GB** (Perfil Mínimo) e para o **job de desempenho do CI**. No notebook de produção, medições só em **janela de manutenção, com backup verificado e em banco separado** do banco de produção, com dados sintéticos (D-22; Volume 13 §7). Testes destrutivos (queda de energia, disco cheio, atualização com reversão) não são feitos no notebook depois que ele entra em produção: vão para a VM. O que é medido em cada release:

| Teste | Como | Critério |
|---|---|---|
| Carga | k6 de outra máquina da rede: 10 usuários virtuais com o roteiro típico (busca, leitura de QR, empréstimo, devolução, consulta), 60 conexões SSE abertas, base com 100 mil movimentações geradas por script | RNF-05 no Perfil Mínimo |
| Memória | Soma do RSS de cada serviço em repouso, sob carga e durante backup e tarefas pesadas (`ops/medir-recursos.sh`) | ≤ 1,5 GB normal; ≤ 2,0 GB no pico (RNF-20); sem uso de swap em operação normal |
| Disco | `iostat` durante carga e durante backup; tempo de resposta durante o backup | Respostas dentro do RNF-05 mesmo com o backup rodando com prioridade baixa |
| Partida a frio | Reiniciar o notebook e medir até a primeira resposta | < 5 min (RNF-06) |
| Queda de energia | Desligar da tomada com a bateria removida ou descarregada, durante gravação | Volta sozinho; nenhum dado confirmado perdido; banco íntegro |
| Disco cheio | Encher o disco até o limite de alerta em homologação | Alerta enviado; sistema recusa novos uploads com mensagem clara; banco continua íntegro |
| Restauração | Restaurar o backup em outra máquina só com o manual | RTO ≤ 4 h; RPO ≤ 15 min (RNF-07) |
| Atualização | N-1 → N e reversão N → N-1 | Sem perda; volta automática se o health check falhar (RNF-14) |

**No CI** (para pegar regressões antes do notebook): um job de desempenho roda a API em contêiner limitado a 2 CPUs e 2 GB, com a base de 100 mil movimentações, e falha se o p95 das rotas principais piorar mais de 20% em relação à referência registrada. Consultas novas passam por `EXPLAIN` automático, que falha em varredura sequencial de tabelas grandes (Volume 04 §4.3).

## 4. Matriz de aparelhos

Definida na R0 (tarefa R0-08) com aparelhos que os membros da Avante realmente usam. Mínimo:

| Classe | Exemplo de critério |
|---|---|
| Android de entrada | 3 GB de RAM, Android 12+, Chrome atual |
| Android intermediário | 6 GB de RAM, Android 14+ |
| iPhone | iOS 17+ com Safari |
| Tablet | Android ou iPad, usado no balcão |
| Notebook | Windows e Linux, Chrome, Edge e Firefox |
| Leitor USB de código de barras | Modelo comum do mercado, modo teclado |
| Impressora de etiquetas | A definida no Volume 08 §3.3 |

Os mesmos três aparelhos de referência (entrada, intermediário, tablet) servem para medir a inferência de visão computacional (RNF-23).

## 5. Casos obrigatórios (todas as releases em que se aplicam)

- **Arquivos:** upload inválido, gigante, com MIME falso, imagem com dimensões excessivas, PDF malicioso.
- **QR e códigos:** duplicado, desconhecido, malformado, de outra organização, revogado, do MVP, lido duas vezes em seguida.
- **NF-e:** malformada, repetida, com itens divergentes, com quantidade fracionária, assinatura ausente.
- **Empréstimos:** retirada, devolução parcial, atraso, renovação, perda/baixa, transferência, devolução com ocorrência.
- **Acesso:** login, logout, expiração, revogação de sessão, força bruta, MFA, troca de papel durante a sessão.
- **Autorização:** para **cada** rota, acesso horizontal (outro usuário, outro almoxarifado) e vertical (papel inferior) negado; inclui rotas de dispositivo.
- **Datas:** servidor em fuso diferente de UTC; virada de dia; horário de verão em outro fuso (RNF-16).
- **Visão computacional:** foto escura, desfocada, com peças sobrepostas, sem peças, com objeto estranho; sempre há caminho manual.
- **Dispositivos:** cartão não vinculado, credencial revogada, leitor sem rede, eventos repetidos.
- **Recursos:** operação com o servidor sob carga e durante o backup.

## 6. Critérios por release (gates)

Uma release só começa quando a anterior está aprovada pelo responsável com as evidências abaixo. O conteúdo funcional de cada release está no Volume 12.

| Release | Critérios de saída (todos com evidência) |
|---|---|
| **R0 — Fundação** | Hardware verificado (Volume 04 §3) e decisão de criptografia registrada · teste de carga sintético no notebook dentro do orçamento (tarefa R0-05) · HTTPS válido e câmera lendo QR em celular real dentro e fora da rede · protótipo aprovado após teste com 5 usuários · CI bloqueante verde (Linux; testes da camada de plataforma também em Windows) · pacote `.deb` instalando em VM limpa e no notebook · backup e restauração de banco vazio funcionando |
| **R1 — Núcleo** | Todos os requisitos M da R1 com testes · autorização testada em todas as rotas · ZAP baseline sem achado alto · RNF-05, RNF-06, RNF-07, RNF-14 e RNF-20 medidos no notebook · 1ª rodada de usabilidade feita e problemas graves corrigidos · uso real paralelo ao MVP sem perda de dados por 4 semanas |
| **R2 — Completo** | Todos os requisitos M e S da R2 · importação do MVP ensaiada em ambiente isolado com totais conciliados e aprovada · revisão heurística, auditoria de acessibilidade e 2ª rodada de usabilidade · pentest interno (ASVS L2) sem achado alto/crítico aberto · checklist de paridade do Anexo A1 100% · **MVP aposentado** com cópia arquivada |
| **R3 — Inteligente** | Cada recurso de visão atinge o RNF-23 no protocolo do Volume 05 §5, ou fica desativado · bancada do leitor de cartão 100% (Volume 05 §7) · relatório de impacto à proteção de dados para cartões · testes de usabilidade de J11–J13 |
| **R4 — Comercial** | Instalação, atualização, reversão e restauração em Linux **e** Windows feitas por alguém que não é o desenvolvedor, só com o manual · restauração cruzada Linux ↔ Windows · pentest externo independente sem achado alto/crítico aberto · textos jurídicos revisados por advogado · análise de homologação Anatel concluída para a Estação Avante · um cliente piloto externo instalado e operando sem participação do desenvolvedor, com aceite formal |

## 7. Definição de Pronto (por tarefa)

Uma tarefa só é concluída quando:
1. O comportamento descrito no requisito funciona e foi demonstrado em homologação.
2. Há testes nas camadas aplicáveis (§2), incluindo os casos de erro e de autorização.
3. O CI está verde sem nenhuma etapa mascarada.
4. As telas cumprem a Definição de Pronto de UI (Volume 07 §18) e seguem o design aprovado no Claude Design.
5. Migrations testadas de vazio e de N-1; rollback possível ou justificativa registrada.
6. Nenhum aumento de memória ou de tempo de resposta acima do orçamento (job de desempenho do CI).
7. Documentação afetada atualizada (manual, API, volumes) no mesmo commit.
8. Auditoria registrada para toda ação que altera dados.
9. Autorrevisão pelo checklist do §8 feita.

## 8. Checklist de autorrevisão

- [ ] Li o diff inteiro como se fosse de outra pessoa.
- [ ] Toda entrada externa é validada no servidor.
- [ ] Toda rota nova tem teste de autorização horizontal e vertical.
- [ ] Nenhuma alteração de saldo acontece fora do ledger.
- [ ] Operações repetíveis usam `Idempotency-Key`.
- [ ] Datas em UTC no banco e formatadas por uma única função no app.
- [ ] Nenhum segredo, dado pessoal real ou caminho local no código ou nos testes.
- [ ] Consultas novas têm índice adequado e passam pelo `EXPLAIN` do CI.
- [ ] Mensagens de erro úteis para a pessoa e sem detalhes internos.
- [ ] Dependência nova tem licença permitida (ADR-016) e justificativa.
- [ ] Mudança de risco alto: segunda leitura no dia seguinte feita.

## 9. Registro de evidências

Cada release tem uma pasta `docs/evidencias/<release>/` com: relatório do CI, relatórios de carga e de recursos do notebook, relatório de avaliação de visão computacional, resultados de usabilidade (sem dados pessoais dos participantes), relatório do ZAP, checklist ASVS, registro de restauração e o termo de aprovação do responsável. Evidência com dado pessoal fica fora do repositório público.
